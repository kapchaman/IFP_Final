using MemoryPalace.Web.Domain.Entities;

namespace MemoryPalace.Web.Services;

public interface IConceptService
{
    Task<IReadOnlyList<Concept>> GetAllAsync(string? search = null, CancellationToken cancellationToken = default);
    Task<Concept?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Concept> CreateAsync(string title, string description, string category, CancellationToken cancellationToken = default);
    Task<Concept> UpdateAsync(Guid id, string title, string description, string category, CancellationToken cancellationToken = default);
    Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default);
    Task ConnectAsync(Guid source, Guid target, RelationshipType relationship, string? note, CancellationToken cancellationToken = default);
    Task DisconnectAsync(Guid id, CancellationToken cancellationToken = default);
    Task<string> ExportAsync(CancellationToken cancellationToken = default);
    Task ImportAsync(string json, CancellationToken cancellationToken = default);
}
