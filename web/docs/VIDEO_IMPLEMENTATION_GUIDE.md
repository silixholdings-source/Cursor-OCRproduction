# AI ERP Demo Video Implementation Guide

## Overview
This guide explains how to implement and customize the demo video modal in your AI ERP application.

## Files Created

### 1. Demo Video Modal Component
**File**: `web/src/components/modals/demo-video-modal.tsx`
- Reusable modal component for displaying demo videos
- Supports YouTube, Vimeo, and self-hosted videos
- Includes play button, feature list, and call-to-action buttons

### 2. Demo Video Button Component
**File**: `web/src/components/demo-video-button.tsx`
- Easy-to-use button component that opens the demo video modal
- Multiple variants and sizes available
- Includes icon-only version

### 3. Video Production Guide
**File**: `web/docs/VIDEO_PRODUCTION_GUIDE.md`
- Complete script and timeline for creating the demo video
- Technical specifications and production checklist
- Alternative implementation options

### 4. Placeholder Video
**File**: `web/public/videos/demo-placeholder.html`
- Temporary placeholder while you create the actual video
- Professional design with feature highlights
- Direct links to interactive demo and contact

## Quick Start

### 1. Add Demo Video Button to Your Homepage

```tsx
// In your homepage component (e.g., web/src/app/page.tsx)
import { DemoVideoButton } from '@/components/demo-video-button'

export default function HomePage() {
  return (
    <div>
      {/* Your existing content */}
      
      {/* Add this button anywhere you want the demo video */}
      <DemoVideoButton 
        variant="default" 
        size="lg"
        className="bg-blue-600 hover:bg-blue-700"
      >
        <Play className="h-5 w-5" />
        Watch Demo Video
      </DemoVideoButton>
    </div>
  )
}
```

### 2. Add Icon Button to Navigation

```tsx
// In your navigation component
import { DemoVideoIconButton } from '@/components/demo-video-button'

export function Navigation() {
  return (
    <nav>
      {/* Your existing navigation items */}
      <DemoVideoIconButton className="ml-4" />
    </nav>
  )
}
```

### 3. Replace Placeholder with Actual Video

Once you have your video ready:

```tsx
// In web/src/components/modals/demo-video-modal.tsx
const videoUrl = "https://www.youtube.com/embed/YOUR_VIDEO_ID" // Replace with your video
```

## Video Hosting Options

### Option 1: YouTube (Recommended)
**Pros**: Free, reliable, good SEO, analytics
**Cons**: YouTube branding, ads possible
**Implementation**:
```tsx
const videoUrl = "https://www.youtube.com/embed/YOUR_VIDEO_ID"
```

### Option 2: Vimeo
**Pros**: Professional, no ads, custom branding
**Cons**: Paid plans for advanced features
**Implementation**:
```tsx
const videoUrl = "https://player.vimeo.com/video/YOUR_VIDEO_ID"
```

### Option 3: Self-hosted
**Pros**: Full control, no external dependencies
**Cons**: Bandwidth costs, hosting complexity
**Implementation**:
```tsx
const videoUrl = "/videos/ai-erp-demo.mp4"
```

## Customization Options

### 1. Video URL Configuration
```tsx
// In demo-video-modal.tsx
const videoUrl = "YOUR_VIDEO_URL_HERE"

// For YouTube with specific parameters
const videoUrl = "https://www.youtube.com/embed/YOUR_VIDEO_ID?autoplay=1&rel=0&modestbranding=1"

// For Vimeo with specific parameters
const videoUrl = "https://player.vimeo.com/video/YOUR_VIDEO_ID?autoplay=1&title=0&byline=0&portrait=0"
```

### 2. Feature List Customization
```tsx
// In demo-video-modal.tsx, update the features array
const features = [
  "3-minute walkthrough of invoice processing",
  "Real-time AI-powered data extraction", 
  "Approval workflow demonstration",
  "ERP integration examples",
  // Add your custom features here
]
```

### 3. Button Styling
```tsx
// Custom button with your styling
<DemoVideoButton 
  variant="outline"
  size="lg"
  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 hover:from-blue-700 hover:to-purple-700"
>
  <Play className="h-5 w-5" />
  Watch Our Demo
</DemoVideoButton>
```

## Integration Examples

### 1. Homepage Hero Section
```tsx
export function HeroSection() {
  return (
    <section className="hero">
      <h1>Transform Your Business with AI ERP</h1>
      <p>See how our platform can revolutionize your invoice processing</p>
      <div className="flex gap-4">
        <DemoVideoButton size="lg">Watch Demo</DemoVideoButton>
        <Button variant="outline" size="lg">Try Free Trial</Button>
      </div>
    </section>
  )
}
```

### 2. Features Section
```tsx
export function FeaturesSection() {
  return (
    <section className="features">
      <h2>Key Features</h2>
      <div className="grid grid-cols-3 gap-6">
        <FeatureCard 
          title="AI Processing"
          description="Intelligent data extraction"
          action={<DemoVideoButton variant="ghost">See in Action</DemoVideoButton>}
        />
        {/* More feature cards */}
      </div>
    </section>
  )
}
```

### 3. Pricing Page
```tsx
export function PricingPage() {
  return (
    <div className="pricing">
      <h1>Choose Your Plan</h1>
      <div className="pricing-cards">
        <PricingCard 
          title="Starter"
          price="$99/month"
          action={<DemoVideoButton>See Demo</DemoVideoButton>}
        />
        {/* More pricing cards */}
      </div>
    </div>
  )
}
```

## Analytics Integration

### Track Video Engagement
```tsx
// In demo-video-modal.tsx
const handlePlay = () => {
  // Track video play event
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'video_play', {
      event_category: 'engagement',
      event_label: 'demo_video'
    })
  }
  setIsPlaying(true)
}

const handleTryInteractiveDemo = () => {
  // Track CTA click
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'click', {
      event_category: 'engagement',
      event_label: 'try_interactive_demo'
    })
  }
  onTryInteractiveDemo()
  handleClose()
}
```

## Testing Checklist

- [ ] Video loads and plays correctly
- [ ] Modal opens and closes properly
- [ ] "Try Interactive Demo" button navigates correctly
- [ ] Responsive design works on mobile
- [ ] Video autoplay works (if enabled)
- [ ] Analytics tracking works (if implemented)
- [ ] Accessibility features work (keyboard navigation, screen readers)

## Troubleshooting

### Video Not Playing
1. Check video URL format
2. Verify video is publicly accessible
3. Check browser console for errors
4. Test with different browsers

### Modal Not Opening
1. Check if component is properly imported
2. Verify state management
3. Check for JavaScript errors

### Performance Issues
1. Optimize video file size
2. Use appropriate video format (MP4)
3. Consider lazy loading for large videos

## Next Steps

1. **Create your demo video** following the production guide
2. **Upload to your chosen platform** (YouTube, Vimeo, or self-host)
3. **Update the video URL** in the modal component
4. **Test thoroughly** across different devices and browsers
5. **Monitor analytics** to measure engagement
6. **Iterate based on feedback** and performance data

## Support

If you need help with implementation:
1. Check the video production guide for content creation
2. Review the component code for customization options
3. Test with the placeholder first before adding your video
4. Monitor browser console for any errors

Remember: The goal is to create an engaging demo that clearly shows your product's value and encourages users to try the interactive demo or contact your sales team.





































