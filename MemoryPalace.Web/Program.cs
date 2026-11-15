using MemoryPalace.Web.Data;
using MemoryPalace.Web.Services;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

if (builder.Environment.IsDevelopment())
{
    // Windows Event Log may be unavailable to a normal local developer account.
    builder.Logging.ClearProviders();
    builder.Logging.AddConsole();
    builder.Logging.AddFilter("Microsoft.AspNetCore.DataProtection", LogLevel.None);
    builder.Services.AddSingleton<IDataProtectionProvider>(new EphemeralDataProtectionProvider());
}

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();

var databaseDirectory = Path.Combine(builder.Environment.ContentRootPath, "App_Data");
Directory.CreateDirectory(databaseDirectory);
var databasePath = Path.Combine(databaseDirectory, "memory-palace.db");

builder.Services.AddDbContextFactory<MemoryPalaceDbContext>(options =>
    options.UseSqlite($"Data Source={databasePath}"));
builder.Services.AddScoped<IConceptService, ConceptService>();
builder.Services.AddScoped<MemoryPalace.Web.State.AtlasState>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
    app.UseHttpsRedirection();
}

app.UseStaticFiles();
app.UseRouting();
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

await using (var scope = app.Services.CreateAsyncScope())
{
    var factory = scope.ServiceProvider.GetRequiredService<IDbContextFactory<MemoryPalaceDbContext>>();
    await using var db = await factory.CreateDbContextAsync();
    await db.Database.EnsureCreatedAsync();
}

app.Run();
