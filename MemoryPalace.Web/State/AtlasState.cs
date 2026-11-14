using MemoryPalace.Web.Domain.Entities;
using MemoryPalace.Web.Services;

namespace MemoryPalace.Web.State;

/// <summary>Scoped to one Blazor circuit; database operations use independent contexts.</summary>
public sealed class AtlasState(IConceptService service)
{
    public IReadOnlyList<Concept> Concepts { get; private set; } = Array.Empty<Concept>();
    public IReadOnlyList<Concept> Visible { get; private set; } = Array.Empty<Concept>();
    public IReadOnlyList<string> Categories { get; private set; } = Array.Empty<string>();
    public Guid? SelectedId { get; set; }
    public Concept? Selected => Concepts.FirstOrDefault(x => x.Id == SelectedId);
    public string Search { get; private set; } = "";
    public string Category { get; private set; } = "";
    public int ConnectionCount { get; private set; }
    public event Action? Changed;

    public async Task ReloadAsync()
    {
        Concepts = await service.GetAllAsync();
        Categories = Concepts.Select(x => x.Category).Distinct().OrderBy(x => x).ToList();
        ConnectionCount = Concepts.Sum(x => x.OutgoingConnections.Count);
        if (Selected is null) SelectedId = null;
        if (!Categories.Contains(Category)) Category = "";
        Filter(Search, Category);
    }

    public void Filter(string search, string category)
    {
        Search = search;
        Category = category;
        Visible = Concepts.Where(x => (string.IsNullOrWhiteSpace(category) || x.Category == category)
            && (string.IsNullOrWhiteSpace(search) || x.Title.Contains(search.Trim(), StringComparison.OrdinalIgnoreCase)
                || x.Description.Contains(search.Trim(), StringComparison.OrdinalIgnoreCase)
                || x.Category.Contains(search.Trim(), StringComparison.OrdinalIgnoreCase))).ToList();
        Changed?.Invoke();
    }
}
