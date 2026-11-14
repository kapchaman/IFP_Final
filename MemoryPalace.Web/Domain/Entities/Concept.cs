namespace MemoryPalace.Web.Domain.Entities;

public sealed class Concept
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Category { get; set; } = "General";
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAtUtc { get; set; } = DateTime.UtcNow;

    public ICollection<Connection> OutgoingConnections { get; set; } = new List<Connection>();
    public ICollection<Connection> IncomingConnections { get; set; } = new List<Connection>();
}
