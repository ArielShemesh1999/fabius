---
name: fabius-decor-flutter-animating-apps
description: Implement animated effects, transitions, and motion in Flutter apps for native iOS/Android motion design.
triggers:
  - "flutter animation"
  - "flutter motion"
  - "mobile animation"
  - "flutter transitions"
---

# flutter-animating-apps

## When to use

Use when a Flutter screen needs motion: page transitions, micro-interactions, loading states, list item animations, or hero transitions between routes.

## Flutter animation primitives

| Need | API |
|------|-----|
| Simple one-shot animation | `AnimationController` + `Tween` |
| Implicit animation (auto) | `AnimatedContainer`, `AnimatedOpacity`, `TweenAnimationBuilder` |
| Staggered list animations | `AnimationController` + `Interval` within a list builder |
| Physics-based motion | `SpringSimulation`, `FrictionSimulation` |
| Hero/shared-element transition | `Hero` widget with matching `tag` |
| Page route transition | Custom `PageRouteBuilder` with `transitionsBuilder` |
| Lottie / JSON animation | `lottie` package — `Lottie.asset('anim.json')` |

## Steps

1. **Choose the right layer** — prefer implicit animations (`Animated*` widgets) for simple state-driven changes. Use `AnimationController` only when you need explicit timing control (stagger, reverse, repeat).
2. **Set up the controller** (when needed):
   ```dart
   late final AnimationController _ctrl;

   @override
   void initState() {
     super.initState();
     _ctrl = AnimationController(
       vsync: this, // requires SingleTickerProviderStateMixin
       duration: const Duration(milliseconds: 300),
     );
   }

   @override
   void dispose() {
     _ctrl.dispose();
     super.dispose();
   }
   ```
3. **Define the tween**:
   ```dart
   final Animation<double> _opacity = Tween(begin: 0.0, end: 1.0)
       .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
   ```
4. **Drive the animation** — call `_ctrl.forward()`, `_ctrl.reverse()`, or `_ctrl.repeat()` in response to state changes or lifecycle events.
5. **For staggered lists** — use `Interval` to offset each item's animation window within the same controller duration:
   ```dart
   Animation<Offset> itemAnim(int index) => Tween<Offset>(
     begin: const Offset(0, 0.3),
     end: Offset.zero,
   ).animate(CurvedAnimation(
     parent: _ctrl,
     curve: Interval(index * 0.1, index * 0.1 + 0.4, curve: Curves.easeOut),
   ));
   ```
6. **For page transitions** — override `PageRouteBuilder.transitionsBuilder`:
   ```dart
   PageRouteBuilder(
     pageBuilder: (_, __, ___) => const NextScreen(),
     transitionsBuilder: (_, anim, __, child) =>
       FadeTransition(opacity: anim, child: child),
     transitionDuration: const Duration(milliseconds: 250),
   )
   ```
7. **Test on device** — enable `debugPaintLayerBordersEnabled` or use Flutter DevTools' performance overlay to confirm 60 fps and no jank.

## Output

Flutter widget(s) with smooth, performant animations that run at 60 fps on target devices, with controllers properly disposed to avoid memory leaks.
