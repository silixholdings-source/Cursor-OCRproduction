# AI ERP SaaS Application - Project Rules

## 🚀 Core Development Standards

### **RULE 1: All Buttons and Links Must Be Functional**
**CRITICAL REQUIREMENT:** Every button and link in the application must have proper functionality implemented.

#### ✅ **Required Standards:**

1. **Button Functionality:**
   - Every `<Button>` component MUST have an `onClick` handler or `asChild` with proper Link component
   - NO placeholder implementations (console.log, alert, etc.)
   - NO disabled buttons without proper disabled state styling
   - All buttons must provide user feedback (loading states, success/error messages)

2. **Link Functionality:**
   - Every `<Link>` component MUST have a valid `href` attribute
   - NO empty href (`href=""`) or placeholder href (`href="#"`)
   - All internal links must use Next.js `Link` component
   - External links must open in new tab with `target="_blank"`

3. **Navigation Consistency:**
   - All navigation buttons must use `useRouter().push()` for internal navigation
   - NO `window.location.href` for internal navigation (except specific cases like redirects)
   - All mobile navigation must close the menu after navigation

#### 🔍 **Implementation Checklist:**

Before committing any code with buttons or links, verify:

- [ ] Button has proper `onClick` handler with actual functionality
- [ ] Link has valid `href` pointing to existing route/page
- [ ] Loading states are implemented for async operations
- [ ] Error handling is implemented with user feedback
- [ ] Accessibility attributes are present (aria-label, title, etc.)
- [ ] Mobile responsiveness is tested
- [ ] Navigation works correctly on all screen sizes

#### 🚫 **Prohibited Patterns:**

```typescript
// ❌ NEVER DO THIS
<Button onClick={() => console.log('clicked')}>Submit</Button>
<Button onClick={() => alert('Not implemented')}>Action</Button>
<Link href="">Broken Link</Link>
<Link href="#">Placeholder</Link>

// ✅ ALWAYS DO THIS
<Button onClick={handleSubmit} disabled={isLoading}>
  {isLoading ? 'Submitting...' : 'Submit'}
</Button>
<Link href="/dashboard/invoices">View Invoices</Link>
```

#### 📋 **Testing Requirements:**

1. **Manual Testing:**
   - Test every button click in development
   - Verify all links navigate to correct pages
   - Test on mobile and desktop
   - Verify loading states and error handling

2. **Code Review Checklist:**
   - All buttons have functional onClick handlers
   - All links have valid href attributes
   - Error handling is implemented
   - Loading states are present
   - Accessibility is maintained

### **RULE 2: Consistent Button Styling**
All buttons must follow the established design system:

#### **Primary CTA Buttons:**
```typescript
className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
```

#### **Secondary CTA Buttons:**
```typescript
className="bg-white text-blue-600 hover:bg-gray-100 border border-blue-600 transition-all duration-200 hover:scale-105 shadow-lg"
```

### **RULE 3: Error Handling Standards**
- All async operations must have try-catch blocks
- User feedback must be provided via toast notifications
- Loading states must be shown during operations
- Fallback data should be provided when APIs fail

### **RULE 4: Accessibility Requirements**
- All interactive elements must have proper ARIA labels
- Focus states must be visible and consistent
- Screen reader compatibility must be maintained
- Keyboard navigation must work for all elements

### **RULE 5: Mobile Responsiveness**
- All buttons must work on touch devices
- Minimum touch target size: 44px x 44px
- Mobile navigation must close after selection
- Responsive design must be tested on multiple screen sizes

## 🔧 Development Workflow

### **Before Adding New Buttons/Links:**
1. Verify the target page/functionality exists
2. Implement proper error handling
3. Add loading states if needed
4. Test on mobile and desktop
5. Add accessibility attributes

### **Before Committing:**
1. Run through all buttons/links in the affected areas
2. Test navigation flows
3. Verify error handling works
4. Check mobile responsiveness
5. Ensure no console errors

### **Code Review Focus:**
- Button functionality implementation
- Link href validation
- Error handling completeness
- Accessibility compliance
- Mobile responsiveness

## 📚 Examples

### **Good Button Implementation:**
```typescript
const [isLoading, setIsLoading] = useState(false)
const { toast } = useToast()

const handleSubmit = async () => {
  setIsLoading(true)
  try {
    await submitData()
    toast({ title: "Success", description: "Data submitted successfully" })
  } catch (error) {
    toast({ title: "Error", description: "Failed to submit data", variant: "destructive" })
  } finally {
    setIsLoading(false)
  }
}

return (
  <Button onClick={handleSubmit} disabled={isLoading}>
    {isLoading ? 'Submitting...' : 'Submit'}
  </Button>
)
```

### **Good Link Implementation:**
```typescript
import Link from 'next/link'
import { useRouter } from 'next/navigation'

// Internal navigation
<Link href="/dashboard/invoices">View Invoices</Link>

// Programmatic navigation
const router = useRouter()
<Button onClick={() => router.push('/dashboard/invoices')}>Go to Invoices</Button>

// External link
<Link href="https://example.com" target="_blank" rel="noopener noreferrer">
  External Resource
</Link>
```

---

## 🎯 **REMEMBER: Every button and link must provide real value to the user. No placeholders, no broken functionality, no exceptions.**

This rule ensures the application maintains professional standards and provides a seamless user experience across all interactions.

