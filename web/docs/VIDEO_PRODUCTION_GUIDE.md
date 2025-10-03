# AI ERP Demo Video Production Guide

## Video Requirements
- **Duration**: 3-4 minutes total
- **Resolution**: 1920x1080 (Full HD) minimum
- **Format**: MP4 (H.264 codec)
- **Aspect Ratio**: 16:9
- **Frame Rate**: 30fps

## Video Script & Timeline

### 1. Introduction (0:00 - 0:15)
**Visual**: Logo animation, clean background
**Narration**: 
> "Welcome to AI ERP - the intelligent enterprise resource planning platform that transforms how businesses process invoices and manage approvals. Let me show you how our AI-powered system works in just 3 minutes."

### 2. Invoice Processing Walkthrough (0:15 - 2:00)
**Visual**: Screen recording of the actual application

#### 2.1 Upload Process (0:15 - 0:45)
- Show the invoice upload interface
- Demonstrate dragging and dropping an invoice file
- Show the file being processed with a loading indicator
- Highlight the "AI Processing" status

#### 2.2 AI Data Extraction (0:45 - 1:30)
- Show the OCR results appearing in real-time
- Highlight extracted fields:
  - Vendor name
  - Invoice number
  - Date
  - Amount
  - Line items
- Show confidence scores for each field
- Demonstrate the AI highlighting uncertain fields

#### 2.3 Data Validation (1:30 - 2:00)
- Show the system flagging potential errors
- Demonstrate manual correction of AI suggestions
- Show the final validated data ready for approval

### 3. Real-time AI-Powered Data Extraction (2:00 - 2:45)
**Visual**: Close-up of the AI extraction process

#### 3.1 Multiple Document Types (2:00 - 2:20)
- Show processing different invoice formats
- Demonstrate handling of handwritten notes
- Show extraction from PDF, image, and scanned documents

#### 3.2 AI Learning (2:20 - 2:45)
- Show the system learning from corrections
- Demonstrate improved accuracy over time
- Highlight the confidence scoring system

### 4. Approval Workflow Demonstration (2:45 - 3:30)
**Visual**: Workflow interface and notifications

#### 4.1 Workflow Setup (2:45 - 3:00)
- Show the approval chain configuration
- Demonstrate role-based permissions
- Show approval thresholds and rules

#### 4.2 Approval Process (3:00 - 3:30)
- Show notifications being sent to approvers
- Demonstrate mobile approval interface
- Show approval/rejection with comments
- Highlight the audit trail

### 5. ERP Integration Examples (3:30 - 4:00)
**Visual**: Integration dashboard and data flow

#### 5.1 System Integration (3:30 - 3:45)
- Show connection to popular ERP systems (SAP, Oracle, QuickBooks)
- Demonstrate data synchronization
- Show real-time updates across systems

#### 5.2 Call to Action (3:45 - 4:00)
- Show the "Try Interactive Demo" button
- Display contact information
- End with logo and tagline

## Technical Implementation

### Video Hosting Options

#### Option 1: YouTube (Recommended)
```typescript
const videoUrl = "https://www.youtube.com/embed/YOUR_VIDEO_ID"
```

#### Option 2: Vimeo
```typescript
const videoUrl = "https://player.vimeo.com/video/YOUR_VIDEO_ID"
```

#### Option 3: Self-hosted
```typescript
const videoUrl = "/videos/ai-erp-demo.mp4"
```

### Integration Code

Update the modal component with your actual video URL:

```typescript
// In web/src/components/modals/demo-video-modal.tsx
const videoUrl = "YOUR_ACTUAL_VIDEO_URL_HERE"
```

## Production Checklist

### Pre-Production
- [ ] Prepare demo data and test invoices
- [ ] Set up clean, professional screen recording environment
- [ ] Prepare script and practice narration
- [ ] Test all application features to be demonstrated
- [ ] Prepare backup scenarios for different invoice types

### Recording
- [ ] Use high-quality screen recording software (OBS, Camtasia, or similar)
- [ ] Record at 1920x1080 resolution minimum
- [ ] Use clear, professional narration
- [ ] Ensure smooth mouse movements and clicks
- [ ] Record in a quiet environment
- [ ] Use consistent lighting if including face cam

### Post-Production
- [ ] Edit for smooth transitions
- [ ] Add professional intro/outro graphics
- [ ] Include captions for accessibility
- [ ] Optimize file size for web delivery
- [ ] Test video playback on different devices
- [ ] Create thumbnail image

### Testing
- [ ] Test video playback in the modal
- [ ] Verify autoplay functionality
- [ ] Test on different browsers and devices
- [ ] Ensure video loads quickly
- [ ] Test the "Try Interactive Demo" button functionality

## Video Content Guidelines

### Visual Style
- Clean, modern interface
- Consistent color scheme matching your brand
- Professional typography
- Smooth animations and transitions
- Clear call-to-action buttons

### Narration Style
- Professional but friendly tone
- Clear pronunciation
- Appropriate pacing (not too fast or slow)
- Emphasize key benefits and features
- Use active voice and present tense

### Key Messages
1. **Efficiency**: "Save hours of manual data entry"
2. **Accuracy**: "AI-powered extraction with 99%+ accuracy"
3. **Integration**: "Seamlessly connects with your existing ERP"
4. **Workflow**: "Streamlined approval process"
5. **ROI**: "See results in days, not months"

## Implementation Steps

1. **Create the video** following the script above
2. **Upload to your chosen platform** (YouTube, Vimeo, or self-host)
3. **Update the video URL** in the modal component
4. **Test the integration** on your website
5. **Gather feedback** from users and iterate

## Alternative: Interactive Demo

If creating a video is not feasible immediately, you can:

1. **Use the existing interactive demo** at `/demo/interactive`
2. **Create a guided tour** with tooltips and highlights
3. **Use animated GIFs** to show key features
4. **Implement a step-by-step walkthrough** in the application

## Success Metrics

Track these metrics to measure video effectiveness:
- Video completion rate
- Click-through rate to "Try Interactive Demo"
- Time spent on demo page
- Conversion rate from video to trial signup
- User feedback and comments

Remember: The goal is to clearly demonstrate the value proposition and encourage users to try the interactive demo or contact your sales team.





































