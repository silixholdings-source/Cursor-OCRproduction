import { render, screen } from '@testing-library/react'
import { Logo } from '../logo'

describe('Logo', () => {
  it('renders logo with text by default', () => {
    render(<Logo />)
    
    expect(screen.getByText('AI ERP')).toBeInTheDocument()
    expect(screen.getByText('SaaS')).toBeInTheDocument()
  })

  it('renders logo without text when showText is false', () => {
    render(<Logo showText={false} />)
    
    expect(screen.queryByText('AI ERP')).not.toBeInTheDocument()
    expect(screen.queryByText('SaaS')).not.toBeInTheDocument()
  })

  it('renders as a link to home page', () => {
    render(<Logo />)
    
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/')
  })

  it('applies custom className', () => {
    render(<Logo className="custom-class" />)
    
    const link = screen.getByRole('link')
    expect(link).toHaveClass('custom-class')
  })
})
