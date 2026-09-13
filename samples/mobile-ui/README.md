# Mobile App UI — Meditation App

Pixel-perfect UI mockup for a meditation mobile app. Four screens:
onboarding, home, streaks, library.

## Screens

1. **Onboarding** — welcome + 3 category cards + CTA
2. **Home** — greeting + streak widget + today's pick + start session
3. **Streaks** — current streak + week calendar + achievements
4. **Library** — categories grid + bottom nav

## Design system

- **Typography:** Inter (system default on iOS/Android)
- **Colors:** amber/red gradient for streaks, neutral grays for structure
- **Spacing:** 16/24/32 px scale
- **Corners:** 12-16px radius (friendly, approachable)
- **Icons:** emoji for fast iteration, swap to SF Symbols / Material Icons in production

## Why HTML mockup instead of Figma?

For early-stage founders, **HTML mockups beat Figma** because:
- They're interactive (founder can click through)
- They're viewable in any browser (no Figma account)
- They translate directly to production code
- I can ship the real React Native app from this mockup in days

## Production-ready upgrades

- React Native + Expo implementation
- SF Symbols / Material Icons
- Local notifications for streak reminders
- In-app purchases via RevenueCat
- Backend: Supabase or Firebase
