# Kilele Project - Hiking App

## Project Overview
React Native mobile app built with Expo (SDK 53) for discovering and exploring hiking trails in Kenya. Currently in early development with a basic hike selection interface.

## Tech Stack
- **Framework**: React Native 0.79.2 with Expo ~53.0.9
- **React Version**: 19.0.0 (latest)
- **Build System**: Expo with new architecture enabled (`newArchEnabled: true`)
- **Supported Platforms**: iOS, Android, Web

## Project Structure
```
HikingApp/
├── App.js              # Main app component with hike list UI
├── index.js            # Entry point (registerRootComponent)
├── app.json            # Expo configuration
├── package.json        # Dependencies and scripts
└── assets/             # Images (icon.png, splash-icon.png, etc.)
```

## Development Workflow

### Running the App (Development)
- `npm start` or `expo start` - Start development server
- `npm run android` - Launch on Android emulator/device
- `npm run ios` - Launch on iOS simulator/device  
- `npm run web` - Launch in browser

### Deployment & Distribution

#### Prerequisites
```bash
# Install EAS CLI globally
npm install -g eas-cli

# Login to Expo account (create one at expo.dev)
eas login
```

#### Initial Setup (One-time)
```bash
# Configure project for EAS Build
eas build:configure

# This creates eas.json with build profiles
```

#### Building for Production

**Android APK (for testing)**:
```bash
eas build --platform android --profile preview
```

**iOS Development Build**:
```bash
eas build --platform ios --profile development
```

**Production Builds (App Store/Play Store)**:
```bash
# Android (AAB for Play Store)
eas build --platform android --profile production

# iOS (requires Apple Developer account $99/year)
eas build --platform ios --profile production
```

#### Submitting to App Stores
```bash
# Submit Android to Google Play
eas submit --platform android

# Submit iOS to App Store (requires Apple Developer account)
eas submit --platform ios
```

#### Web Deployment
```bash
# Build web version
npx expo export --platform web

# Deploy to Netlify/Vercel
# - Install Netlify CLI: npm i -g netlify-cli
# - Deploy: netlify deploy --dir=dist --prod
# Or connect GitHub repo to Netlify/Vercel for auto-deployment
```

#### Over-the-Air (OTA) Updates
```bash
# Update JavaScript/assets without app store review
eas update --branch production --message "Bug fixes"

# Configure in app.json:
# "updates": { "url": "https://u.expo.dev/[your-project-id]" }
```

#### Testing Distribution
- **Android**: Share APK file directly or use Google Play Internal Testing
- **iOS**: Use TestFlight (requires Apple Developer account)
- **Expo Go**: Development testing only, not for production

### Architecture Notes
- **Entry Point**: `index.js` uses `registerRootComponent(App)` for Expo compatibility
- **Data**: Currently using in-file hardcoded `hikeData` array in `App.js`
- **Navigation**: Placeholder console.log handlers - navigation library not yet implemented
- **State Management**: Local component state only (no Redux/Context yet)

## Code Conventions

### Styling
- StyleSheet API for all styles (no inline styles)
- Consistent style object naming: `container`, `title`, `hikeListContainer`, `hikeItem`, `hikeItemText`
- Cross-platform shadows: combine `elevation` (Android) with `shadowColor/shadowOffset/shadowOpacity/shadowRadius` (iOS)

### Component Patterns
- Functional components with hooks (no class components)
- Event handlers use descriptive names: `handleHikePress`, not generic `onPress`
- Component file structure: imports → data → component → styles

### Data Structure
```javascript
// Current hike data format
{ 
  id: string,      // Unique identifier
  name: string     // Display name (Kenyan hiking locations)
}
```

## Development Roadmap

### Phase 1: Core Navigation & Details (Current)
- [ ] Implement React Navigation library
- [ ] Build hike detail screens with full trail information
- [ ] Add custom hiking imagery to assets
- [ ] Move `hikeData` to separate data service layer

### Phase 2: Backend Integration
- [ ] Set up backend API for trail data (consider Firebase/Supabase or custom Node.js)
- [ ] Implement data fetching with proper loading/error states
- [ ] Add offline data caching for trail information
- [ ] User authentication system (email/social login)

### Phase 3: Advanced Features
- [ ] GPS tracking and location services integration
- [ ] Interactive trail maps (Google Maps/Mapbox)
- [ ] Photo upload and gallery for trails
- [ ] Trail difficulty ratings and user reviews
- [ ] Social features: share hikes, follow hikers, create groups
- [ ] Offline map downloads for trail navigation

### Phase 4: Enhanced UX
- [ ] Push notifications for weather alerts and trail updates
- [ ] Trail completion tracking and achievement badges
- [ ] Emergency contact integration
- [ ] Multi-language support (English, Swahili)

## Platform-Specific Notes
- **iOS**: Tablet support enabled (`supportsTablet: true`)
- **Android**: Edge-to-edge display enabled, adaptive icons configured
- **Web**: Basic web support via Expo (favicon configured)
- New React Native architecture enabled for all platforms

## When Adding Features

### Data Layer
- Keep Kenyan hiking focus (existing trails: Mount Kenya, Ngong Hills, Karura Forest, Aberdare Ranges, Hell's Gate)
- Plan for rich trail data: GPS coordinates, elevation profiles, difficulty levels, estimated duration, safety info
- Design API schema to support offline-first architecture

### UI/UX Guidelines
- Follow existing shadow/elevation pattern for card-style UI elements
- Maintain nature-inspired color palette (greens, earth tones)
- Ensure accessibility: minimum touch targets 44x44pt, proper contrast ratios
- Use React Native best practices: FlatList for long lists, Image optimization, avoid unnecessary re-renders

### Navigation
- Install React Navigation before building detail screens
- Structure: Stack Navigator (main) → Tab Navigator (home/profile/map) → Individual screens
- Deep linking support for sharing specific trails

### Performance
- Lazy load images with proper placeholder states
- Implement pagination for trail lists as data grows
- Monitor bundle size (consider code splitting for maps/camera features)
- Test on lower-end Android devices (not just emulators)
