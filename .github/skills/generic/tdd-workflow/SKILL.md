---
name: tdd-workflow
description: >
  Drive a TDD RED-GREEN-REFACTOR loop with stack-aware test framework (xUnit or NUnit for .NET,
  Jest + RTL for React Web, Jest + RNTL for React Native, flutter_test + bloc_test for Flutter).
  Enforces Arrange/Act/Assert,
  ≥80% coverage on new code, one logical assertion per test (related asserts OK; unrelated → split). Use when the user wants to start a
  new feature test-first or asks for tests-before-implementation.
origin: ADNOC (mirror of ECC dotnet-patterns shape)
---

# TDD Workflow

The RED → GREEN → REFACTOR loop, installed in **every** repo for whoever opts into test-first.
Whether feature work is *required* to be test-first is set per repo by the `test_discipline`
answer (that rule lives in the stack instructions, not here) — so on a `tests-required` or
`lenient` repo this is an on-request capability, not a mandate. When invoked, it forces the
model into RED → GREEN → REFACTOR instead of writing tests after code (which is what AI tends
to do unprompted).

## When to Activate

- User says "let's TDD this" / "tests first" / "write the test before the code"
- New feature work on a repo whose `test_discipline` is `tdd`, or an explicit per-task ask
- An orchestrator or QA flow delegates test-writing for a feature (the `orchestrator` agent's Verify phase, or the optional spec-driven orchestrator noted in `ai/specs/README.md` — not shipped by default)
- A bug-fix workflow needs a failing test first (`/fix-bug` step 1)

## The Loop (One Cycle)

### RED — write a failing test

1. Identify ONE concrete requirement from the spec (or one symptom of the bug)
2. Write a test that asserts the requirement / reproduces the symptom
3. Run the test — it MUST fail. If it passes immediately, your test is wrong or the requirement
   is already covered. Stop and reconsider.
4. Output the test code + the failure message verbatim

### GREEN — minimal code to make it pass

1. Write the SMALLEST possible change that flips the test to pass
2. No anticipation of future requirements. No "while I'm here" extras.
3. Run the test — it must pass
4. Run the whole test suite — nothing else breaks
5. Output the diff + the pass message

### REFACTOR — improve without changing behavior

1. Look at the GREEN code. Is it the natural shape? Or hack-grade?
2. Apply ONE refactor that keeps all tests green (rename, extract, dedupe)
3. Re-run all tests after every refactor
4. Output the diff + final test count

### Loop or stop

If more requirements remain: back to RED with the next one.
If done: write the coverage report + summary.

## Stack-Specific Framework

### .NET — xUnit OR NUnit

Both frameworks are in use across the org. Match whatever the repo (or the existing test
project) already uses — never assume xUnit-only. The example below is xUnit; the NUnit
equivalent is `[Test]` / `[TestCase(...)]` with `[SetUp]` instead of a constructor.

```csharp
public class OrderServiceTests
{
    private readonly IOrderRepository _repo = Substitute.For<IOrderRepository>();

    [Fact] // NUnit: [Test]
    public async Task CreateOrder_WithValidInput_ReturnsOrderId()
    {
        // Arrange
        var sut = new OrderService(_repo);
        var input = new CreateOrderRequest("SKU-1", 2);

        // Act
        var result = await sut.CreateAsync(input, CancellationToken.None);

        // Assert
        result.Should().BeGreaterThan(0);
    }

    [Theory] // NUnit: [TestCase("", 1)] etc. over a [Test]
    [InlineData("", 1)]
    [InlineData("SKU-1", 0)]
    [InlineData("SKU-1", -1)]
    public async Task CreateOrder_WithInvalidInput_Throws(string sku, int qty)
    {
        // Arrange
        var sut = new OrderService(_repo);

        // Act + Assert
        await FluentActions.Awaiting(() => sut.CreateAsync(new(sku, qty), default))
            .Should().ThrowAsync<ArgumentException>();
    }
}
```

- One `[Fact]` / `[Test]` = one scenario; `[Theory]`+`[InlineData]` (xUnit) or `[TestCase]` (NUnit) for parameterized
- FluentAssertions for readable assertions (including `ThrowAsync` for exceptions)
- NSubstitute for mocking — `Substitute.For<T>()`, `.Returns(...)`, `.Received()`
- No real DB in unit tests — use Testcontainers for the integration tier

#### Adding a dependency to a class under test

When the spec adds a new dependency to the class you are testing, do NOT just patch the one new test:

- Add an NSubstitute substitute field for it and wire it into the SUT constructor (alongside the existing ones)
- Re-check EVERY existing test that exercises the changed code path — if that path now calls the new dependency, stub its return there so the test still drives real behavior
- Keep stubs local to the tests that need them — never push a `.Returns(...)` into shared `[SetUp]` / a shared constructor under strict substitutes (it surfaces as unexpected/unnecessary-call failures)

#### Per-method coverage checklist

For each method touched, cover (only the rows that apply to that method):

- Happy path — valid input produces the expected result
- Dependency called with correct args — assert via `.Received(1)` with argument matchers
- Null / invalid input — guard throws the right exception, dependency NOT called
- Not-found — query-by-id returns null/empty handled correctly (right exception or null result)
- Dependency throws — exception propagates or is wrapped as the project expects
- Mapping completeness — every field the method maps is asserted, not just one
- `CancellationToken` pass-through — the token reaches the dependency calls

### ReactJS Web — Jest + RTL

```tsx
test('clicking Delete fires onDelete with item id', async () => {
  // Arrange
  const onDelete = jest.fn();
  render(<Row item={{ id: '42', name: 'X' }} onDelete={onDelete} />);

  // Act
  await userEvent.click(screen.getByRole('button', { name: /delete/i }));

  // Assert
  expect(onDelete).toHaveBeenCalledWith('42');
});
```

- Query by accessible role / label, NOT by class / test-id (unless nothing else works)
- `userEvent` over `fireEvent` (more realistic)
- MSW for fetch mocking — never global `jest.spyOn(global, 'fetch')`
- One assertion per test (related assertions OK; unrelated → split)

### React Native — Jest + RNTL

```tsx
import { render, screen, userEvent } from '@testing-library/react-native';

test('Pressable shows label after press', async () => {
  render(<Counter />);
  const button = screen.getByRole('button', { name: /increment/i });
  await userEvent.press(button);
  expect(screen.getByText('Count: 1')).toBeOnTheScreen();
});
```

- `jest-expo` preset for Expo projects; `react-native` preset for bare
- `transformIgnorePatterns` extended for `react-native` package
- Mock native modules at the top of the test file (`jest.mock` module-level; `jest.fn()` per test)
- `userEvent` over `fireEvent`
- **Never import `ReactDOM`** or web DOM matchers — RNTL only; web assertions silently lie on RN
- Platform branches: `jest.spyOn(Platform, 'OS', 'get').mockReturnValue('ios')` (RN defines
  `Platform.OS` as a getter — `jest.replaceProperty` rejects accessors) — test BOTH platforms
  when behavior diverges
- Mock hygiene: `jest.clearAllMocks()` in `afterEach` (or `clearMocks: true` in config) — leaked mocks = flaky suite
- `act()` only for state updates outside `fireEvent`/`userEvent` (e.g. `useEffect` side effects) — not as a blanket wrapper
- Mock navigation with `jest.mock('@react-navigation/native')` — never render a full navigator in a unit test

### Flutter — flutter_test + bloc_test

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';

void main() {
  // Unit / widget test — pump the widget, assert on rendered output
  testWidgets('Counter shows incremented value after tap', (tester) async {
    // Arrange
    await tester.pumpWidget(const MaterialApp(home: CounterPage()));

    // Act
    await tester.tap(find.byTooltip('increment'));
    await tester.pumpAndSettle();

    // Assert
    expect(find.text('Count: 1'), findsOneWidget);
  });

  // Cubit/Bloc test — assert the emitted state sequence, not internals
  blocTest<CounterCubit, int>(
    'emits [1] when increment() is called',
    build: () => CounterCubit(),
    act: (cubit) => cubit.increment(),
    expect: () => const [1],
  );
}
```

- `flutter_test` for unit + widget tests; `blocTest` (from `bloc_test`) for a Cubit/Bloc —
  assert the emitted state sequence over `build` / `act` / `expect`, never the Cubit's internals
- Widget tests pump with the providers the screen needs (`BlocProvider`, `get_it` overrides,
  localization delegates); settle async UI with `await tester.pumpAndSettle()`
- Mock collaborators (repositories, `dio`, services) — no real network, file, or platform calls
- **Determinism:** no real timers/clocks/random — drive time with `fakeAsync` or an injected
  clock, and call `getIt.reset()` between tests (in `tearDown`) so locator state never leaks
- `patrol` drives `integration_test/` E2E flows — keep it out of the unit/widget tier

## Coverage Bar

- ≥ 80% line coverage on new code merged in this PR
- Coverage measured by Coverlet (.NET) / Jest (`--coverage`) / `flutter test --coverage` (Flutter) — all shipped in `verify` skill
- 100% on critical paths (payment, auth, data export)

## Anti-Patterns to Avoid

| Pattern | Why | Fix |
|---|---|---|
| Test written AFTER code | Misses edge cases the spec already implied | RED first |
| Skipping RED (write test that already passes) | Doesn't prove the test discriminates | Make it red first, then green |
| Multiple unrelated assertions in one test | Hard to debug; one failure hides others | Split into multiple tests |
| Mocking the system under test | You're testing the mock, not the code | Mock dependencies only |
| Test names like "test1" / "shouldWork" | Useless on failure | `MethodName_Scenario_ExpectedResult` |
| Hard-coded `Thread.Sleep` for async | Flaky | `await` / `WaitForAsync` |
| Real DB / network in unit tests | Slow + flaky | In-memory / Testcontainers / mocks |
| Snapshot test of an entire DOM tree | Breaks on every change, no signal | Targeted assertions on rendered text/roles |
| `setTimeout` in tests for "wait for state" | Race condition | `await waitFor(...)` from RTL |

## Outputs Expected from This Skill

When invoked by an orchestrator or a tester sub-agent:

- A list of test file paths added / modified
- A `req# → test name` mapping for every spec requirement
- The exact `verify` output showing all tests pass
- A coverage delta (`+X% line coverage on new files`)

Return raw facts, not prose.
