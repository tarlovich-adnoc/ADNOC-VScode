---
name: dotnet-patterns
description: Idiomatic C#/.NET patterns — records, init-only setters, async with CancellationToken, constructor DI, Options pattern, Dapper data access (SQL Server + MongoDB), minimal APIs, guard clauses. Use when the user writes, reviews, or refactors C#/.NET code (.cs files, ASP.NET Core services, Dapper repositories, minimal APIs).
origin: ECC
---

<!--
  Lifted from github.com/affaan-m/ECC (MIT). © 2026 Affaan Mustafa.
  ADNOC adaptation: the data-access section was changed from the original EF Core
  repository to Dapper (IDbConnection) plus a MongoDB/Cosmos point-read, to match the
  org's data-access reality; the rest of the body is kept verbatim for provenance.
  See ai/THIRD-PARTY-NOTICES.md for the full attribution.
-->

# .NET Development Patterns

Idiomatic C# and .NET patterns for building robust, performant, and maintainable applications.

## When to Activate

- Writing new C# code
- Reviewing C# code
- Refactoring existing .NET applications
- Designing service architectures with ASP.NET Core

## Core Principles

### 1. Prefer Immutability

Use records and init-only properties for data models. Mutability should be an explicit, justified choice.

```csharp
// Good: Immutable value object
public sealed record Money(decimal Amount, string Currency);

// Good: Immutable DTO with init setters
public sealed class CreateOrderRequest
{
    public required string CustomerId { get; init; }
    public required IReadOnlyList<OrderItem> Items { get; init; }
}

// Bad: Mutable model with public setters
public class Order
{
    public string CustomerId { get; set; }
    public List<OrderItem> Items { get; set; }
}
```

### 2. Explicit Over Implicit

Be clear about nullability, access modifiers, and intent.

```csharp
// Good: Explicit access modifiers and nullability
public sealed class UserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    public UserService(IUserRepository repository, ILogger<UserService> logger)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<User?> FindByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        return await _repository.FindByIdAsync(id, cancellationToken);
    }
}
```

### 3. Depend on Abstractions

Use interfaces for service boundaries. Register via DI container.

```csharp
// Good: Interface-based dependency
public interface IOrderRepository
{
    Task<Order?> FindByIdAsync(Guid id, CancellationToken cancellationToken);
    Task<IReadOnlyList<Order>> FindByCustomerAsync(string customerId, CancellationToken cancellationToken);
    Task AddAsync(Order order, CancellationToken cancellationToken);
}

// Registration
builder.Services.AddScoped<IOrderRepository, DapperOrderRepository>();
```

## Async/Await Patterns

### Proper Async Usage

```csharp
// Good: Async all the way, with CancellationToken
public async Task<OrderSummary> GetOrderSummaryAsync(
    Guid orderId,
    CancellationToken cancellationToken)
{
    var order = await _repository.FindByIdAsync(orderId, cancellationToken)
        ?? throw new NotFoundException($"Order {orderId} not found");

    var customer = await _customerService.GetAsync(order.CustomerId, cancellationToken);

    return new OrderSummary(order, customer);
}

// Bad: Blocking on async
public OrderSummary GetOrderSummary(Guid orderId)
{
    var order = _repository.FindByIdAsync(orderId, CancellationToken.None).Result; // Deadlock risk
    return new OrderSummary(order);
}
```

### Parallel Async Operations

```csharp
// Good: Concurrent independent operations
public async Task<DashboardData> LoadDashboardAsync(CancellationToken cancellationToken)
{
    var ordersTask = _orderService.GetRecentAsync(cancellationToken);
    var metricsTask = _metricsService.GetCurrentAsync(cancellationToken);
    var alertsTask = _alertService.GetActiveAsync(cancellationToken);

    await Task.WhenAll(ordersTask, metricsTask, alertsTask);

    return new DashboardData(
        Orders: await ordersTask,
        Metrics: await metricsTask,
        Alerts: await alertsTask);
}
```

## Options Pattern

Bind configuration sections to strongly-typed objects.

```csharp
public sealed class SmtpOptions
{
    public const string SectionName = "Smtp";

    public required string Host { get; init; }
    public required int Port { get; init; }
    public required string Username { get; init; }
    public bool UseSsl { get; init; } = true;
}

// Registration
builder.Services.Configure<SmtpOptions>(
    builder.Configuration.GetSection(SmtpOptions.SectionName));

// Usage via injection
public class EmailService(IOptions<SmtpOptions> options)
{
    private readonly SmtpOptions _smtp = options.Value;
}
```

## Repository Pattern with Dapper (SQL Server)

Data access here is Dapper over an `IDbConnection`, not an ORM. Always parameterize — pass
values as an anonymous object or `DynamicParameters`, never concatenate into the SQL text.
For a graph load (the parent plus its children), use Dapper multi-mapping with `splitOn`
instead of an ORM `Include`.

```csharp
public sealed class DapperOrderRepository : IOrderRepository
{
    private readonly IDbConnectionFactory _connectionFactory;

    public DapperOrderRepository(IDbConnectionFactory connectionFactory)
        => _connectionFactory = connectionFactory;

    public async Task<Order?> FindByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT  o.Id, o.CustomerId, o.CreatedAt,
                    i.Id, i.OrderId, i.Sku, i.Quantity
            FROM    Orders o
            LEFT JOIN OrderItems i ON i.OrderId = o.Id
            WHERE   o.Id = @Id;
            """;

        await using var connection = await _connectionFactory.CreateAsync(cancellationToken);

        var ordersById = new Dictionary<Guid, Order>();

        // Multi-mapping: each row is split into (Order, OrderItem) at the "Id" boundary
        // (splitOn), and the children are stitched onto a single parent — the Dapper
        // equivalent of a graph/Include load without the N+1 round-trips.
        var rows = await connection.QueryAsync<Order, OrderItem, Order>(
            new CommandDefinition(sql, new { Id = id }, cancellationToken: cancellationToken),
            (order, item) =>
            {
                if (!ordersById.TryGetValue(order.Id, out var existing))
                {
                    existing = order with { Items = new List<OrderItem>() };
                    ordersById.Add(existing.Id, existing);
                }

                if (item is not null)
                    ((List<OrderItem>)existing.Items).Add(item);

                return existing;
            },
            splitOn: "Id");

        return rows.FirstOrDefault();
    }

    public async Task<IReadOnlyList<Order>> FindByCustomerAsync(
        string customerId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT  Id, CustomerId, CreatedAt
            FROM    Orders
            WHERE   CustomerId = @CustomerId
            ORDER BY CreatedAt DESC;
            """;

        await using var connection = await _connectionFactory.CreateAsync(cancellationToken);

        var orders = await connection.QueryAsync<Order>(
            new CommandDefinition(sql, new { CustomerId = customerId }, cancellationToken: cancellationToken));

        return orders.ToList();
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO Orders (Id, CustomerId, CreatedAt)
            VALUES (@Id, @CustomerId, @CreatedAt);
            """;

        await using var connection = await _connectionFactory.CreateAsync(cancellationToken);

        await connection.ExecuteAsync(
            new CommandDefinition(sql, order, cancellationToken: cancellationToken));
    }
}
```

`QueryFirstOrDefaultAsync<T>` is the right call when a query returns at most one flat row
(no child collection to stitch):

```csharp
public async Task<Customer?> FindCustomerAsync(string customerId, CancellationToken cancellationToken)
{
    const string sql = "SELECT Id, Name, Tier FROM Customers WHERE Id = @CustomerId;";

    await using var connection = await _connectionFactory.CreateAsync(cancellationToken);

    return await connection.QueryFirstOrDefaultAsync<Customer>(
        new CommandDefinition(sql, new { CustomerId = customerId }, cancellationToken: cancellationToken));
}
```

### MongoDB / Cosmos (Mongo API) point read

For document data, a point read is a `Find` filtered by `_id` (which is the partition key in
Cosmos for single-partition collections) — fetch by key, then `FirstOrDefaultAsync`. Keep the
filter on the partition key so the read stays a single-partition lookup, not a fan-out.

```csharp
public sealed class MongoOrderRepository
{
    private readonly IMongoCollection<OrderDocument> _orders;

    public MongoOrderRepository(IMongoDatabase database)
        => _orders = database.GetCollection<OrderDocument>("orders");

    public async Task<OrderDocument?> FindByIdAsync(string id, CancellationToken cancellationToken)
    {
        var filter = Builders<OrderDocument>.Filter.Eq(o => o.Id, id);

        return await _orders
            .Find(filter)
            .FirstOrDefaultAsync(cancellationToken);
    }
}
```

## Middleware and Pipeline

```csharp
// Custom middleware
public sealed class RequestTimingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestTimingMiddleware> _logger;

    public RequestTimingMiddleware(RequestDelegate next, ILogger<RequestTimingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        try
        {
            await _next(context);
        }
        finally
        {
            stopwatch.Stop();
            _logger.LogInformation(
                "Request {Method} {Path} completed in {ElapsedMs}ms with status {StatusCode}",
                context.Request.Method,
                context.Request.Path,
                stopwatch.ElapsedMilliseconds,
                context.Response.StatusCode);
        }
    }
}
```

## Minimal API Patterns

```csharp
// Organized with route groups
var orders = app.MapGroup("/api/orders")
    .RequireAuthorization()
    .WithTags("Orders");

orders.MapGet("/{id:guid}", async (
    Guid id,
    IOrderRepository repository,
    CancellationToken cancellationToken) =>
{
    var order = await repository.FindByIdAsync(id, cancellationToken);
    return order is not null
        ? TypedResults.Ok(order)
        : TypedResults.NotFound();
});

orders.MapPost("/", async (
    CreateOrderRequest request,
    IOrderService service,
    CancellationToken cancellationToken) =>
{
    var order = await service.PlaceOrderAsync(request, cancellationToken);
    return TypedResults.Created($"/api/orders/{order.Id}", order);
});
```

## Guard Clauses

```csharp
// Good: Early returns with clear validation
public async Task<ProcessResult> ProcessPaymentAsync(
    PaymentRequest request,
    CancellationToken cancellationToken)
{
    ArgumentNullException.ThrowIfNull(request);

    if (request.Amount <= 0)
        throw new ArgumentOutOfRangeException(nameof(request.Amount), "Amount must be positive");

    if (string.IsNullOrWhiteSpace(request.Currency))
        throw new ArgumentException("Currency is required", nameof(request.Currency));

    // Happy path continues here without nesting
    var gateway = _gatewayFactory.Create(request.Currency);
    return await gateway.ChargeAsync(request, cancellationToken);
}
```

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|---|---|
| `async void` methods | Return `Task` (except event handlers) |
| `.Result` or `.Wait()` | Use `await` |
| `catch (Exception) { }` | Handle or rethrow with context |
| `new Service()` in constructors | Use constructor injection |
| `public` fields | Use properties with appropriate accessors |
| `dynamic` in business logic | Use generics or explicit types |
| Mutable `static` state | Use DI scoping or `ConcurrentDictionary` |
| `string.Format` in loops | Use `StringBuilder` or interpolated string handlers |

<!-- ADNOC additions (not part of the verbatim ECC lift) — org reality: Dapper data access, SQL Server + MongoDB. -->

| Anti-Pattern | Fix |
|---|---|
| N+1 with Dapper — a per-row query inside a `foreach` over results | One query (a join projected into the result) or Dapper multi-mapping (`QueryAsync<A, B, ...>` with `splitOn`) |
| Raw SQL built by string concatenation / interpolation | Pass values as Dapper parameters (`new { id }` / `DynamicParameters`) — never concatenate user input into the SQL text |
| `new HttpClient()` in a request path | Inject a typed/named client from `IHttpClientFactory` (socket exhaustion / stale DNS) |
| Binding or returning a raw DB entity from a controller | Bind a request DTO and return a response DTO — guards against mass-assignment / over-posting |
