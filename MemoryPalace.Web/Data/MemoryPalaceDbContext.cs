using MemoryPalace.Web.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace MemoryPalace.Web.Data;

public sealed class MemoryPalaceDbContext : DbContext
{
    public MemoryPalaceDbContext(DbContextOptions<MemoryPalaceDbContext> options) : base(options) { }

    public DbSet<Concept> Concepts => Set<Concept>();
    public DbSet<Connection> Connections => Set<Connection>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Concept>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Title).HasMaxLength(100).IsRequired();
            entity.Property(x => x.Description).HasMaxLength(2000);
            entity.Property(x => x.Category).HasMaxLength(40).IsRequired();
            entity.HasIndex(x => x.Title);
            entity.HasIndex(x => x.Category);
        });

        modelBuilder.Entity<Connection>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Relationship).HasConversion<string>().HasMaxLength(24);
            entity.Property(x => x.Note).HasMaxLength(500);
            entity.HasOne(x => x.SourceConcept)
                .WithMany(x => x.OutgoingConnections)
                .HasForeignKey(x => x.SourceConceptId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(x => x.TargetConcept)
                .WithMany(x => x.IncomingConnections)
                .HasForeignKey(x => x.TargetConceptId)
                .OnDelete(DeleteBehavior.Restrict);
            entity.HasIndex(x => new { x.SourceConceptId, x.TargetConceptId }).IsUnique();
        });
    }
}
