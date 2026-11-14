using System.Text.Json;
using MemoryPalace.Web.Data;
using MemoryPalace.Web.Domain.Entities;
using MemoryPalace.Web.Services;
using Microsoft.EntityFrameworkCore;

// Real SQLite integration checks. A unique temporary database is removed even after failure.
var path = Path.Combine(Path.GetTempPath(), $"memory-palace-test-{Guid.NewGuid()}.db");
var factory = new TestFactory(new DbContextOptionsBuilder<MemoryPalaceDbContext>().UseSqlite($"Data Source={path};Pooling=False").Options);
var service = new ConceptService(factory);
var count = 0;
void Check(bool condition, string name) { if (!condition) throw new Exception($"FAIL: {name}"); Console.WriteLine($"PASS: {name}"); count++; }
async Task Reject(Func<Task> action, string name)
{
    try { await action(); }
    catch (ArgumentException) { Check(true, name); return; }
    throw new Exception($"FAIL: {name} did not reject invalid input");
}
try
{
    await using (var db = factory.CreateDbContext()) await db.Database.EnsureCreatedAsync();
    var a = await service.CreateAsync("  Атом  ", " Particle ", " Физика ");
    Check(a.Title == "Атом" && a.Description == "Particle" && a.Category == "Физика", "Input is trimmed");
    await Reject(() => service.CreateAsync("АТОМ", "", "General"), "Unicode duplicate title rejected");
    await Reject(() => service.CreateAsync("x", "", "General"), "Short title rejected");
    await Reject(() => service.CreateAsync(new string('x', 101), "", "General"), "Long title rejected");
    await Reject(() => service.CreateAsync("Valid", new string('x', 2001), "General"), "Long description rejected");
    await Reject(() => service.CreateAsync("Valid", "", " "), "Blank category rejected");
    var b = await service.CreateAsync("Molecule", "", "Chemistry");
    var c = await service.CreateAsync("Water", "", "Chemistry");
    var updated = await service.UpdateAsync(a.Id, "Атом", "Updated", "Science");
    Check(updated.CreatedAtUtc == a.CreatedAtUtc && updated.UpdatedAtUtc >= a.UpdatedAtUtc && updated.Description == "Updated", "Update preserves creation time");
    await Reject(() => service.UpdateAsync(a.Id, "Molecule", "", "Science"), "Edit rejects duplicate title");
    await Reject(() => service.UpdateAsync(Guid.NewGuid(), "Absent", "", "Science"), "Edit missing concept rejected");
    await service.ConnectAsync(a.Id, b.Id, RelationshipType.Explains, "  A note  ");
    await service.ConnectAsync(c.Id, a.Id, RelationshipType.Supports, null);
    var all = await service.GetAllAsync();
    Check(all.Sum(x => x.OutgoingConnections.Count) == 2, "Atlas query includes graph edges");
    var detail = (await service.GetByIdAsync(a.Id))!;
    Check(detail.OutgoingConnections.Single().TargetConcept?.Title == b.Title && detail.IncomingConnections.Single().SourceConcept?.Title == c.Title, "Both directions load endpoint details");
    Check(detail.OutgoingConnections.Single().Note == "A note", "Connection note is trimmed");
    await Reject(() => service.ConnectAsync(a.Id, a.Id, RelationshipType.Related, null), "Self connection rejected");
    await Reject(() => service.ConnectAsync(a.Id, Guid.NewGuid(), RelationshipType.Related, null), "Missing endpoint rejected");
    await Reject(() => service.ConnectAsync(a.Id, b.Id, RelationshipType.Supports, null), "Duplicate directed pair rejected");
    await Reject(() => service.ConnectAsync(b.Id, c.Id, (RelationshipType)999, null), "Invalid relationship rejected");
    await Reject(() => service.ConnectAsync(b.Id, c.Id, RelationshipType.Related, new string('n', 501)), "Long note rejected");
    Check((await service.GetAllAsync("АТОМ")).Single().Id == a.Id, "Database search supports Cyrillic case folding");
    var json = await service.ExportAsync();
    await Reject(() => service.ImportAsync(json), "Restore refuses nonempty atlas");
    Check(await service.DeleteAsync(a.Id), "Delete connected concept succeeds");
    all = await service.GetAllAsync();
    Check(all.Count == 2 && all.Sum(x => x.OutgoingConnections.Count) == 0, "Delete removes incoming and outgoing edges");
    Check(!await service.DeleteAsync(a.Id), "Deleting absent concept is harmless");
    await service.DeleteAsync(b.Id);
    await service.DeleteAsync(c.Id);
    await Reject(() => service.ImportAsync("{bad json"), "Malformed JSON rejected");
    await Reject(() => service.ImportAsync("{\"Version\":99,\"Concepts\":[],\"Connections\":[]}"), "Unknown backup version rejected");
    var backup = JsonSerializer.Deserialize<AtlasBackup>(json)!;
    var broken = backup with { Connections = new() { backup.Connections[0] with { TargetConceptId = Guid.NewGuid() } } };
    await Reject(() => service.ImportAsync(JsonSerializer.Serialize(broken)), "Dangling backup connection rejected");
    Check((await service.GetAllAsync()).Count == 0, "Failed import leaves database empty");
    await service.ImportAsync(json);
    all = await service.GetAllAsync();
    Check(all.Count == 3 && all.Sum(x => x.OutgoingConnections.Count) == 2 && all.Any(x => x.Id == a.Id), "Backup round trip preserves IDs and edges");
    await service.DisconnectAsync(all.SelectMany(x => x.OutgoingConnections).First().Id);
    Check((await service.GetAllAsync()).Sum(x => x.OutgoingConnections.Count) == 1, "Disconnect preserves concepts");
    // Multiple readers exercise the factory lifetime without sharing a DbContext.
    var reads = await Task.WhenAll(Enumerable.Range(0, 8).Select(_ => service.GetAllAsync()));
    Check(reads.All(x => x.Count == 3), "Concurrent reads use separate contexts");
    Console.WriteLine($"{count} SQLite integration checks passed.");
}
finally
{
    foreach (var suffix in new[] { "", "-wal", "-shm" }) File.Delete(path + suffix);
}

sealed class TestFactory(DbContextOptions<MemoryPalaceDbContext> options) : IDbContextFactory<MemoryPalaceDbContext>
{
    public MemoryPalaceDbContext CreateDbContext() => new(options);
}
