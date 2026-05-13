import { useRouteError, isRouteErrorResponse } from 'react-router-dom'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'

export function RouteErrorBoundary() {
  const error = useRouteError()

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle>Something went wrong</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-sm text-muted-foreground">
            {isRouteErrorResponse(error)
              ? `Server error ${error.status}: ${error.statusText}`
              : error instanceof Error
              ? error.message
              : 'The page failed to load.'}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => window.location.reload()}>
              Reload page
            </Button>
            <Button variant="ghost" onClick={() => window.history.back()}>
              Go back
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
