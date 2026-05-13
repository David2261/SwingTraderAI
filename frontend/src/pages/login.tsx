import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, LogIn } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { useLogin } from '@/features/auth/hooks/auth-hooks'
import { loginFormSchema, type LoginFormData } from '@/features/auth/schemas/auth-schemas'
import backgroundImage from '@/assets/background.jpg';

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'

  const loginMutation = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginFormSchema),
  })

  const onSubmit = (data: LoginFormData) => {
    loginMutation.mutate(data, {
      onSuccess: () => {
        navigate(from, { replace: true })
      },
    })
  }

  return (
    <div
    className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10"
    style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}>
        <div className="relative z-10 w-full max-w-md">
        <div className="absolute inset-0 bg-[#010825]/50" />
        <div className="absolute rounded-full inset-0 bg-gradient-to-br from-[#001789]/50 via-transparent to-[#1CB4FF]/20" />
        <div className="absolute left-[-120px] top-[-120px] h-[420px] w-[420px] rounded-full bg-[#1CB4FF]/25 blur-3xl" />
        <div className="absolute bottom-[-150px] right-[-100px] h-[380px] w-[380px] rounded-full bg-[#2667FF]/20 blur-3xl" />
        <div className="absolute rounded-full left-1/2 top-1/2 h-[300px] w-[300px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/5 blur-3xl" />
        <Card className="
            relative
            w-full
            max-w-md
            overflow-hidden
            rounded-3xl
            border
            border-white/10
            bg-white/10
            shadow-2xl
            backdrop-blur-2xl
            supports-[backdrop-filter]:bg-white/10
        ">
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
            <CardHeader className="space-y-2 pb-6">
            <CardTitle className="text-center text-3xl text-white">С возвращением</CardTitle>
            <CardDescription className="text-center text-white/60">
                Введите свои учетные данные для доступа к своему аккаунту.
            </CardDescription>
            </CardHeader>
            <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-white/80">
                    Email
                </label>
                <Input
                id="email"
                type="email"
                placeholder="Введите ваш email"
                className="
                    border-white/10
                    bg-white/5
                    text-white
                    placeholder:text-white/40
                    backdrop-blur-xl
                    focus-visible:border-[#1CB4FF]
                    input-glow
                "
                {...register('email')}
                />
                {errors.email && (
                    <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
                </div>

                <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                    Пароль
                </label>
                <div className="relative">
                    <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Введите пароль"
                    className="
                    pr-10
                    border-white/10
                    bg-white/5
                    text-white
                    placeholder:text-white/40
                    backdrop-blur-xl
                    focus-visible:border-[#1CB4FF]
                    input-glow
                    "
                    {...register('password')}
                    />
                    <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="
                    absolute right-0 top-0 h-full px-3 py-2
                    text-white/50
                    hover:bg-transparent
                    hover:text-white
                    "
                    onClick={() => setShowPassword(!showPassword)}
                    >
                    {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                    ) : (
                        <Eye className="h-4 w-4" />
                    )}
                    </Button>
                </div>
                {errors.password && (
                    <p className="text-sm text-red-300">{errors.password.message}</p>
                )}
                </div>

                <Button
                type="submit"
                className="
                    h-11
                    w-full
                    border-0
                    bg-gradient-to-r
                    from-[#1CB4FF]
                    to-[#2667FF]
                    text-white
                    shadow-lg
                    shadow-blue-500/30
                    transition-all
                    duration-300
                    hover:scale-[1.01]
                    hover:shadow-blue-500/50
                "
                disabled={loginMutation.isPending}
                >
                {loginMutation.isPending ? (
                    <div className="flex items-center space-x-2">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    <span>Вход...</span>
                    </div>
                ) : (
                    <div className="flex items-center space-x-2">
                    <LogIn className="h-4 w-4" />
                    <span>Вход</span>
                    </div>
                )}
                </Button>
            </form>

            <div className="mt-6 text-center text-sm">
                <span className="text-white/50">Ещё нет аккаунта? </span>
                <Link
                to="/register"
                className="font-medium text-[#1CB4FF] transition-colors hover:text-white"
                >
                Регистрация сейчас
                </Link>
            </div>
            </CardContent>
        </Card>
        </div>
    </div>
  )
}
