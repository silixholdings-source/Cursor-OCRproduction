import type { Meta, StoryObj } from '@storybook/react'
import { Logo } from './logo'

const meta: Meta<typeof Logo> = {
  title: 'Components/Logo',
  component: Logo,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    showText: {
      control: 'boolean',
      description: 'Whether to show the text label',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {},
}

export const WithoutText: Story = {
  args: {
    showText: false,
  },
}

export const WithCustomClass: Story = {
  args: {
    className: 'text-2xl',
  },
}
