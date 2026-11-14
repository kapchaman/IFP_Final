using System.Text.Json;
using MemoryPalace.Web.Data;
using MemoryPalace.Web.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace MemoryPalace.Web.Services;

public sealed class ConceptService(IDbContextFactory<MemoryPalaceDbContext> factory) : IConceptService
{
    public async Task<IReadOnlyList<Concept>> GetAllAsync(string? search = null, CancellationToken cancellationToken = default)
    {
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        var concepts = await db.Concepts.AsNoTracking().Include(x => x.OutgoingConnections)
            .OrderBy(x => x.Title).ToListAsync(cancellationToken);
        if (string.IsNullOrWhiteSpace(search)) return concepts;
        var term = search.Trim();
        return concepts.Where(x => x.Title.Contains(term, StringComparison.OrdinalIgnoreCase)
            || x.Description.Contains(term, StringComparison.OrdinalIgnoreCase)
            || x.Category.Contains(term, StringComparison.OrdinalIgnoreCase)).ToList();
    }

    public async Task<Concept?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        return await db.Concepts.AsNoTracking()
            .Include(x => x.OutgoingConnections).ThenInclude(x => x.TargetConcept)
            .Include(x => x.IncomingConnections).ThenInclude(x => x.SourceConcept)
            .AsSplitQuery().FirstOrDefaultAsync(x => x.Id == id, cancellationToken);
    }

    public Task<Concept> CreateAsync(string title, string description, string category, CancellationToken cancellationToken = default) =>
        SaveAsync(null, title, description, category, cancellationToken);

    public Task<Concept> UpdateAsync(Guid id, string title, string description, string category, CancellationToken cancellationToken = default) =>
        SaveAsync(id, title, description, category, cancellationToken);

    private async Task<Concept> SaveAsync(Guid? id, string title, string description, string category, CancellationToken cancellationToken)
    {
        (title, description, category) = Validate(title, description, category);
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        await using var transaction = await db.Database.BeginTransactionAsync(cancellationToken);
        var titles = await db.Concepts.Where(x => x.Id != id).Select(x => x.Title).ToListAsync(cancellationToken);
        if (titles.Any(x => string.Equals(x, title, StringComparison.OrdinalIgnoreCase)))
            throw new ArgumentException("A concept with this title already exists.");
        var concept = id.HasValue
            ? await db.Concepts.SingleOrDefaultAsync(x => x.Id == id, cancellationToken)
                ?? throw new ArgumentException("This concept no longer exists. Refresh your atlas.")
            : new Concept();
        concept.Title = title;
        concept.Description = description;
        concept.Category = category;
        concept.UpdatedAtUtc = DateTime.UtcNow;
        if (!id.HasValue) db.Concepts.Add(concept);
        await db.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        return concept;
    }

    public async Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        await using var transaction = await db.Database.BeginTransactionAsync(cancellationToken);
        var concept = await db.Concepts.FindAsync(new object[] { id }, cancellationToken);
        if (concept is null) return false;
        // Remove both directions before the target-side restrictive foreign key is checked.
        await db.Connections.Where(x => x.SourceConceptId == id || x.TargetConceptId == id).ExecuteDeleteAsync(cancellationToken);
        db.Concepts.Remove(concept);
        await db.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        return true;
    }

    public async Task ConnectAsync(Guid source, Guid target, RelationshipType relationship, string? note, CancellationToken cancellationToken = default)
    {
        note = note?.Trim();
        if (source == target) throw new ArgumentException("Choose a different concept to connect.");
        if (!Enum.IsDefined(relationship)) throw new ArgumentException("Choose a valid relationship.");
        if (note?.Length > 500) throw new ArgumentException("Notes cannot exceed 500 characters.");
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        await using var transaction = await db.Database.BeginTransactionAsync(cancellationToken);
        if (await db.Concepts.CountAsync(x => x.Id == source || x.Id == target, cancellationToken) != 2)
            throw new ArgumentException("One of these concepts no longer exists. Refresh your atlas.");
        if (await db.Connections.AnyAsync(x => x.SourceConceptId == source && x.TargetConceptId == target, cancellationToken))
            throw new ArgumentException("These concepts are already connected in this direction.");
        db.Connections.Add(new Connection { SourceConceptId = source, TargetConceptId = target, Relationship = relationship, Note = note });
        await db.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);
    }

    public async Task DisconnectAsync(Guid id, CancellationToken cancellationToken = default)
    {
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        await db.Connections.Where(x => x.Id == id).ExecuteDeleteAsync(cancellationToken);
    }

    public async Task<string> ExportAsync(CancellationToken cancellationToken = default)
    {
        // One query gives a consistent snapshot without serializing EF navigation cycles.
        var concepts = await GetAllAsync(cancellationToken: cancellationToken);
        var backup = new AtlasBackup(1,
            concepts.Select(x => new ConceptRecord(x.Id, x.Title, x.Description, x.Category, x.CreatedAtUtc, x.UpdatedAtUtc)).ToList(),
            concepts.SelectMany(x => x.OutgoingConnections).Select(x => new ConnectionRecord(x.Id, x.SourceConceptId, x.TargetConceptId, x.Relationship, x.Note)).ToList());
        return JsonSerializer.Serialize(backup, new JsonSerializerOptions { WriteIndented = true });
    }

    public async Task ImportAsync(string json, CancellationToken cancellationToken = default)
    {
        AtlasBackup backup;
        try { backup = JsonSerializer.Deserialize<AtlasBackup>(json) ?? throw new ArgumentException("The backup is empty."); }
        catch (JsonException) { throw new ArgumentException("Choose a valid Memory Palace JSON backup."); }
        if (backup.Version != 1 || backup.Concepts is null || backup.Connections is null)
            throw new ArgumentException("Unsupported or incomplete backup.");
        if (backup.Concepts.Count > 2000 || backup.Connections.Count > 10000)
            throw new ArgumentException("Backups support up to 2,000 concepts and 10,000 connections.");
        var concepts = new List<Concept>();
        var ids = new HashSet<Guid>();
        var titles = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var item in backup.Concepts)
        {
            if (item is null) throw new ArgumentException("The backup contains an empty concept.");
            var (title, description, category) = Validate(item.Title, item.Description, item.Category);
            if (item.Id == Guid.Empty || !ids.Add(item.Id) || !titles.Add(title))
                throw new ArgumentException("The backup contains duplicate titles or invalid concept IDs.");
            if (item.CreatedAtUtc == default || item.UpdatedAtUtc < item.CreatedAtUtc)
                throw new ArgumentException("The backup contains invalid concept dates.");
            concepts.Add(new Concept { Id = item.Id, Title = title, Description = description, Category = category,
                CreatedAtUtc = item.CreatedAtUtc, UpdatedAtUtc = item.UpdatedAtUtc });
        }
        var pairs = new HashSet<(Guid, Guid)>();
        var edgeIds = new HashSet<Guid>();
        var connections = new List<Connection>();
        foreach (var item in backup.Connections)
        {
            if (item is null || item.Id == Guid.Empty || !edgeIds.Add(item.Id) || !ids.Contains(item.SourceConceptId)
                || !ids.Contains(item.TargetConceptId) || item.SourceConceptId == item.TargetConceptId
                || !pairs.Add((item.SourceConceptId, item.TargetConceptId)) || !Enum.IsDefined(item.Relationship) || item.Note?.Length > 500)
                throw new ArgumentException("The backup contains an invalid or duplicate connection.");
            connections.Add(new Connection { Id = item.Id, SourceConceptId = item.SourceConceptId,
                TargetConceptId = item.TargetConceptId, Relationship = item.Relationship, Note = item.Note?.Trim() });
        }
        await using var db = await factory.CreateDbContextAsync(cancellationToken);
        await using var transaction = await db.Database.BeginTransactionAsync(cancellationToken);
        if (await db.Concepts.AnyAsync(cancellationToken))
            throw new ArgumentException("Restore requires an empty atlas. Export your current atlas before clearing it.");
        db.Concepts.AddRange(concepts);
        db.Connections.AddRange(connections);
        await db.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);
    }

    private static (string Title, string Description, string Category) Validate(string? title, string? description, string? category)
    {
        title = (title ?? "").Trim().Normalize();
        description = (description ?? "").Trim();
        category = (category ?? "").Trim().Normalize();
        if (title.Length is < 2 or > 100) throw new ArgumentException("Title must contain between 2 and 100 characters.");
        if (description.Length > 2000) throw new ArgumentException("Description cannot exceed 2,000 characters.");
        if (category.Length is < 2 or > 40) throw new ArgumentException("Category must contain between 2 and 40 characters.");
        return (title, description, category);
    }
}

public sealed record AtlasBackup(int Version, List<ConceptRecord> Concepts, List<ConnectionRecord> Connections);
public sealed record ConceptRecord(Guid Id, string Title, string Description, string Category, DateTime CreatedAtUtc, DateTime UpdatedAtUtc);
public sealed record ConnectionRecord(Guid Id, Guid SourceConceptId, Guid TargetConceptId, RelationshipType Relationship, string? Note);
