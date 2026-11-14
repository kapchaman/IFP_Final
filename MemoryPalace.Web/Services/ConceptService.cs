using MemoryPalace.Web.Data;
using MemoryPalace.Web.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace MemoryPalace.Web.Services;

public sealed class ConceptService
{
    private readonly MemoryPalaceDbContext _db;

    public ConceptService(MemoryPalaceDbContext db) => _db = db;

    public async Task<IReadOnlyList<Concept>> GetAllAsync(string? search = null, CancellationToken cancellationToken = default)
    {
        var query = _db.Concepts.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(search))
        {
            var term = search.Trim();
            query = query.Where(x => x.Title.Contains(term) || x.Description.Contains(term) || x.Category.Contains(term));
        }

        return await query.OrderBy(x => x.Title).ToListAsync(cancellationToken);
    }

    public async Task<Concept?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default) =>
        await _db.Concepts.AsNoTracking()
            .Include(x => x.OutgoingConnections).ThenInclude(x => x.TargetConcept)
            .Include(x => x.IncomingConnections).ThenInclude(x => x.SourceConcept)
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);

    public async Task<Concept> CreateAsync(string title, string description, string category, CancellationToken cancellationToken = default)
    {
        title = (title ?? string.Empty).Trim();
        description = (description ?? string.Empty).Trim();
        category = (category ?? string.Empty).Trim();

        if (title.Length is < 2 or > 100)
            throw new ArgumentException("Title must contain between 2 and 100 characters.", nameof(title));
        if (description.Length > 2000)
            throw new ArgumentException("Description cannot exceed 2,000 characters.", nameof(description));
        if (category.Length is < 2 or > 40)
            throw new ArgumentException("Category must contain between 2 and 40 characters.", nameof(category));

        var duplicate = await _db.Concepts.AnyAsync(x => x.Title.ToLower() == title.ToLower(), cancellationToken);
        if (duplicate)
            throw new InvalidOperationException("A concept with this title already exists.");

        var concept = new Concept { Title = title, Description = description, Category = category };
        _db.Concepts.Add(concept);
        await _db.SaveChangesAsync(cancellationToken);
        return concept;
    }

    public async Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var concept = await _db.Concepts.FindAsync(new object[] { id }, cancellationToken);
        if (concept is null) return false;

        _db.Concepts.Remove(concept);
        await _db.SaveChangesAsync(cancellationToken);
        return true;
    }
}
