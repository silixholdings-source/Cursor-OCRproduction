"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { format } from "date-fns"
import { CalendarIcon, Upload, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

const invoiceSchema = z.object({
  invoiceNumber: z.string().min(1, "Invoice number is required"),
  supplierName: z.string().min(1, "Supplier name is required"),
  supplierEmail: z.string().email("Invalid email address").optional().or(z.literal("")),
  totalAmount: z.string().min(1, "Total amount is required"),
  currency: z.string().min(1, "Currency is required"),
  invoiceDate: z.date({
    required_error: "Invoice date is required",
  }),
  dueDate: z.date().optional(),
  description: z.string().optional(),
  department: z.string().optional(),
  costCenter: z.string().optional(),
  projectCode: z.string().optional(),
  poNumber: z.string().optional(),
  tags: z.array(z.string()).optional(),
  file: z.any().optional(),
})

type InvoiceFormData = z.infer<typeof invoiceSchema>

interface InvoiceFormProps {
  onSubmit: (data: InvoiceFormData) => void
  onCancel: () => void
  initialData?: Partial<InvoiceFormData>
  loading?: boolean
  mode?: "create" | "edit"
}

export function InvoiceForm({
  onSubmit,
  onCancel,
  initialData,
  loading = false,
  mode = "create"
}: InvoiceFormProps) {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
  const [tags, setTags] = React.useState<string[]>(initialData?.tags || [])
  const [tagInput, setTagInput] = React.useState("")

  const form = useForm<InvoiceFormData>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      invoiceNumber: initialData?.invoiceNumber || "",
      supplierName: initialData?.supplierName || "",
      supplierEmail: initialData?.supplierEmail || "",
      totalAmount: initialData?.totalAmount || "",
      currency: initialData?.currency || "USD",
      invoiceDate: initialData?.invoiceDate || new Date(),
      dueDate: initialData?.dueDate,
      description: initialData?.description || "",
      department: initialData?.department || "",
      costCenter: initialData?.costCenter || "",
      projectCode: initialData?.projectCode || "",
      poNumber: initialData?.poNumber || "",
      tags: initialData?.tags || [],
    },
  })

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      form.setValue("file", file)
    }
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      const newTags = [...tags, tagInput.trim()]
      setTags(newTags)
      form.setValue("tags", newTags)
      setTagInput("")
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    const newTags = tags.filter(tag => tag !== tagToRemove)
    setTags(newTags)
    form.setValue("tags", newTags)
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault()
      handleAddTag()
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {mode === "create" ? "Create New Invoice" : "Edit Invoice"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Invoice Number */}
            <div className="space-y-2">
              <Label htmlFor="invoiceNumber">Invoice Number *</Label>
              <Input
                id="invoiceNumber"
                {...form.register("invoiceNumber")}
                placeholder="Enter invoice number"
              />
              {form.formState.errors.invoiceNumber && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.invoiceNumber.message}
                </p>
              )}
            </div>

            {/* Supplier Name */}
            <div className="space-y-2">
              <Label htmlFor="supplierName">Supplier Name *</Label>
              <Input
                id="supplierName"
                {...form.register("supplierName")}
                placeholder="Enter supplier name"
              />
              {form.formState.errors.supplierName && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.supplierName.message}
                </p>
              )}
            </div>

            {/* Supplier Email */}
            <div className="space-y-2">
              <Label htmlFor="supplierEmail">Supplier Email</Label>
              <Input
                id="supplierEmail"
                type="email"
                {...form.register("supplierEmail")}
                placeholder="Enter supplier email"
              />
              {form.formState.errors.supplierEmail && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.supplierEmail.message}
                </p>
              )}
            </div>

            {/* Total Amount */}
            <div className="space-y-2">
              <Label htmlFor="totalAmount">Total Amount *</Label>
              <div className="flex">
                <Select
                  value={form.watch("currency")}
                  onValueChange={(value) => form.setValue("currency", value)}
                >
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD</SelectItem>
                    <SelectItem value="EUR">EUR</SelectItem>
                    <SelectItem value="GBP">GBP</SelectItem>
                    <SelectItem value="CAD">CAD</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  id="totalAmount"
                  type="number"
                  step="0.01"
                  {...form.register("totalAmount")}
                  placeholder="0.00"
                  className="ml-2"
                />
              </div>
              {form.formState.errors.totalAmount && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.totalAmount.message}
                </p>
              )}
            </div>

            {/* Invoice Date */}
            <div className="space-y-2">
              <Label>Invoice Date *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !form.watch("invoiceDate") && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {form.watch("invoiceDate") ? (
                      format(form.watch("invoiceDate"), "PPP")
                    ) : (
                      <span>Pick a date</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={form.watch("invoiceDate")}
                    onSelect={(date) => form.setValue("invoiceDate", date || new Date())}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              {form.formState.errors.invoiceDate && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.invoiceDate.message}
                </p>
              )}
            </div>

            {/* Due Date */}
            <div className="space-y-2">
              <Label>Due Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !form.watch("dueDate") && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {form.watch("dueDate") ? (
                      format(form.watch("dueDate"), "PPP")
                    ) : (
                      <span>Pick a date</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={form.watch("dueDate")}
                    onSelect={(date) => form.setValue("dueDate", date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* PO Number */}
            <div className="space-y-2">
              <Label htmlFor="poNumber">PO Number</Label>
              <Input
                id="poNumber"
                {...form.register("poNumber")}
                placeholder="Enter PO number"
              />
            </div>

            {/* Department */}
            <div className="space-y-2">
              <Label htmlFor="department">Department</Label>
              <Input
                id="department"
                {...form.register("department")}
                placeholder="Enter department"
              />
            </div>

            {/* Cost Center */}
            <div className="space-y-2">
              <Label htmlFor="costCenter">Cost Center</Label>
              <Input
                id="costCenter"
                {...form.register("costCenter")}
                placeholder="Enter cost center"
              />
            </div>

            {/* Project Code */}
            <div className="space-y-2">
              <Label htmlFor="projectCode">Project Code</Label>
              <Input
                id="projectCode"
                {...form.register("projectCode")}
                placeholder="Enter project code"
              />
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...form.register("description")}
              placeholder="Enter invoice description"
              rows={3}
            />
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 hover:bg-destructive hover:text-destructive-foreground rounded-full p-0.5"
                    aria-label={`Remove ${tag} tag`}
                    title={`Remove ${tag} tag`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Add a tag"
              />
              <Button type="button" onClick={handleAddTag} variant="outline">
                Add
              </Button>
            </div>
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <Label>Invoice File</Label>
            <div className="flex items-center gap-4">
              <Input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.tiff"
                onChange={handleFileChange}
                className="flex-1"
              />
              {selectedFile && (
                <div className="flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  <span className="text-sm text-muted-foreground">
                    {selectedFile.name}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-4 pt-6">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : mode === "create" ? "Create Invoice" : "Update Invoice"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
