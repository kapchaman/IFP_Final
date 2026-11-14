namespace MemoryPalace.Web.Domain.Entities;

public sealed class Connection
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid SourceConceptId { get; set; }
    public Concept? SourceConcept { get; set; }
    public Guid TargetConceptId { get; set; }
    public Concept? TargetConcept { get; set; }
    public RelationshipType Relationship { get; set; } = RelationshipType.Related;
    public string? Note { get; set; }
}

public enum RelationshipType
{
    Related = 0,
    Explains = 1,
    Supports = 2,
    Contradicts = 3,
    ExampleOf = 4
}
