using MemoryPalace.Web.Domain.Entities;
using MemoryPalace.Web.Services;
using MemoryPalace.Web.State;

var a = new Concept { Title = "Атом", Category = "Физика", Description = "Частицы" };
var b = new Concept { Title = "Molecule", Category = "Chemistry" };
var c = new Concept { Title = "Water", Category = "Chemistry" };
var isolated = new Concept { Title = "Music", Category = "Art" };
a.OutgoingConnections.Add(new Connection { SourceConceptId = a.Id, TargetConceptId = b.Id });
b.OutgoingConnections.Add(new Connection { SourceConceptId = b.Id, TargetConceptId = c.Id });
c.OutgoingConnections.Add(new Connection { SourceConceptId = c.Id, TargetConceptId = a.Id });
var nodes = new[] { a, b, c, isolated };
var count = 0;
void Check(bool condition, string name) { if (!condition) throw new Exception($"FAIL: {name}"); Console.WriteLine($"PASS: {name}"); count++; }
Check(GraphExplorer.FindPath(nodes, a.Id, c.Id).SequenceEqual(new[] { a.Id, c.Id }), "Shortest path wins over longer route in a cycle");
Check(GraphExplorer.FindPath(nodes, b.Id, a.Id).SequenceEqual(new[] { b.Id, a.Id }), "Relationships can be traversed backwards");
Check(GraphExplorer.FindPath(nodes, a.Id, a.Id).SequenceEqual(new[] { a.Id }), "Same source and target");
Check(GraphExplorer.FindPath(nodes, a.Id, isolated.Id).Count == 0, "Disconnected graph terminates");
Check(GraphExplorer.FindPath(nodes, Guid.NewGuid(), a.Id).Count == 0, "Missing source");
Check(GraphExplorer.FindPath(nodes, a.Id, Guid.NewGuid()).Count == 0, "Missing destination");
Check(GraphExplorer.FindPath(Array.Empty<Concept>(), a.Id, c.Id).Count == 0, "Empty graph");
a.OutgoingConnections.Add(new Connection { SourceConceptId = a.Id, TargetConceptId = Guid.NewGuid() });
Check(GraphExplorer.FindPath(nodes, a.Id, c.Id).Count == 2, "Dangling edge ignored");
a.OutgoingConnections.Remove(a.OutgoingConnections.Last());
var fake = new FakeService { Items = nodes };
var state = new AtlasState(fake);
var notifications = 0;
state.Changed += () => notifications++;
await state.ReloadAsync();
Check(state.Visible.Count == 4 && state.Categories.Count == 3 && state.ConnectionCount == 3, "State derives global statistics");
Check(notifications == 1, "State notifies subscribers once per reload");
state.Filter("АТОМ", "");
Check(state.Visible.Single().Id == a.Id, "Case insensitive Cyrillic title search");
state.Filter("частицы", "");
Check(state.Visible.Single().Id == a.Id, "Description search");
state.Filter("chemistry", "");
Check(state.Visible.Count == 2, "Category text search");
state.Filter("water", "Физика");
Check(state.Visible.Count == 0, "Search intersects category filter");
state.Filter("  water  ", "Chemistry");
Check(state.Visible.Single().Id == c.Id, "Trimmed search");
state.SelectedId = a.Id;
await state.ReloadAsync();
Check(state.Selected?.Id == a.Id && state.Visible.Single().Id == c.Id, "Reload preserves selection and filters");
fake.Items = new[] { isolated };
await state.ReloadAsync();
Check(state.Selected is null && state.Category == "", "Reload clears removed selection and category");
Check(state.ConnectionCount == 0, "Reload recomputes edges");
Console.WriteLine($"{count} core checks passed.");

sealed class FakeService : IConceptService
{
    public IReadOnlyList<Concept> Items { get; set; } = Array.Empty<Concept>();
    public Task<IReadOnlyList<Concept>> GetAllAsync(string? search = null, CancellationToken cancellationToken = default) => Task.FromResult(Items);
    public Task<Concept?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default) => Task.FromResult(Items.FirstOrDefault(x => x.Id == id));
    public Task<Concept> CreateAsync(string title, string description, string category, CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task<Concept> UpdateAsync(Guid id, string title, string description, string category, CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task ConnectAsync(Guid source, Guid target, RelationshipType relationship, string? note, CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task DisconnectAsync(Guid id, CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task<string> ExportAsync(CancellationToken cancellationToken = default) => throw new NotSupportedException();
    public Task ImportAsync(string json, CancellationToken cancellationToken = default) => throw new NotSupportedException();
}
