using MemoryPalace.Web.Domain.Entities;

namespace MemoryPalace.Web.Services;

/// <summary>Finds the shortest chain, treating relationships as traversable in either direction.</summary>
public static class GraphExplorer
{
    public static IReadOnlyList<Guid> FindPath(IEnumerable<Concept> concepts, Guid source, Guid target)
    {
        var nodes = concepts.ToDictionary(x => x.Id);
        if (!nodes.ContainsKey(source) || !nodes.ContainsKey(target)) return Array.Empty<Guid>();
        var neighbors = nodes.Keys.ToDictionary(x => x, _ => new List<Guid>());
        foreach (var edge in nodes.Values.SelectMany(x => x.OutgoingConnections))
        {
            if (!neighbors.ContainsKey(edge.SourceConceptId) || !neighbors.ContainsKey(edge.TargetConceptId)) continue;
            neighbors[edge.SourceConceptId].Add(edge.TargetConceptId);
            neighbors[edge.TargetConceptId].Add(edge.SourceConceptId);
        }
        var previous = new Dictionary<Guid, Guid?> { [source] = null };
        var queue = new Queue<Guid>();
        queue.Enqueue(source);
        while (queue.TryDequeue(out var current))
        {
            if (current == target)
            {
                var path = new List<Guid>();
                for (Guid? step = target; step.HasValue; step = previous[step.Value]) path.Add(step.Value);
                path.Reverse();
                return path;
            }
            foreach (var next in neighbors[current])
                if (previous.TryAdd(next, current)) queue.Enqueue(next);
        }
        return Array.Empty<Guid>();
    }
}
