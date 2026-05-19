import { PageHeader } from '@/shared/ui/page-header'

export function SettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Настройки"
        description="Управляйте своей учетной записью и настройками."
      />
      <div className="text-center text-muted-foreground">
        Панель настроек появится в ближайшее время....
      </div>
    </div>
  )
}
