import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, UserPlus } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'

import { useRegister } from '@/features/auth/hooks/auth-hooks'
import {
  registerFormSchema,
  type RegisterFormData,
} from '@/features/auth/schemas/auth-schemas'

import backgroundImage from '@/assets/background.jpg'

export function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const navigate = useNavigate()

  const registerMutation = useRegister()

  const {
	register,
	handleSubmit,
	formState: { errors },
  } = useForm<RegisterFormData>({
	resolver: zodResolver(registerFormSchema),
  })

  const onSubmit = (data) => {
  const registerData = {
    username: `${data.first_name}${data.last_name}`.toLowerCase().replace(/\s+/g, ''),
    email: data.email,
    password: data.password,
    telegram_id: null,
  }

  registerMutation.mutate(registerData)
}

  return (
	<div
	  className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10"
	  style={{
		backgroundImage: `url(${backgroundImage})`,
		backgroundSize: 'cover',
		backgroundPosition: 'center',
	  }}
	>
	  <div className="absolute inset-0 bg-[#010825]/40" />
	  <div className="absolute inset-0 bg-gradient-to-br from-[#001789]/40 via-transparent to-[#1CB4FF]/20" />
	  <div className="absolute -left-32 top-0 h-[500px] w-[500px] rounded-full bg-[#1CB4FF]/20 blur-3xl" />
	  <div className="absolute bottom-0 right-0 h-[400px] w-[400px] rounded-full bg-[#2667FF]/20 blur-3xl" />
	  <div className="relative z-10 w-full max-w-lg">
		<Card
		  className="
			relative
			overflow-hidden
			rounded-3xl
			border
			border-white/10
			bg-white/10
			shadow-2xl
			backdrop-blur-2xl
			supports-[backdrop-filter]:bg-white/10
		  "
		>
		  <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />

		  <div className="relative z-10">
			<CardHeader className="space-y-2 pb-6">
			  <CardTitle className="text-center text-3xl text-white">
				Создать аккаунт
			  </CardTitle>

			  <CardDescription className="text-center text-white/60">
				Введите свои данные для создания аккаунта.
			  </CardDescription>
			</CardHeader>

			<CardContent>
			  <form
				onSubmit={handleSubmit(onSubmit)}
				className="space-y-4"
			  >
				<div className="grid grid-cols-2 gap-3">
				  <div className="space-y-2">
					<label
					  htmlFor="firstName"
					  className="text-sm font-medium text-white/80"
					>
					  Имя
					</label>

					<Input
					  id="firstName"
					  placeholder="John"
					  className="
						border-white/10
						bg-white/5
						text-white
						placeholder:text-white/40
						backdrop-blur-xl
						focus-visible:border-[#1CB4FF]
						input-glow
					  "
					  {...register('firstName')}
					/>

					{errors.firstName && (
					  <p className="text-sm text-red-300">
						{errors.firstName.message}
					  </p>
					)}
				  </div>

				  <div className="space-y-2">
					<label
					  htmlFor="lastName"
					  className="text-sm font-medium text-white/80"
					>
					  Фамилия
					</label>

					<Input
					  id="lastName"
					  placeholder="Doe"
					  className="
						border-white/10
						bg-white/5
						text-white
						placeholder:text-white/40
						backdrop-blur-xl
						focus-visible:border-[#1CB4FF]
						input-glow
					  "
					  {...register('lastName')}
					/>

					{errors.lastName && (
					  <p className="text-sm text-red-300">
						{errors.lastName.message}
					  </p>
					)}
				  </div>
				</div>

				<div className="space-y-2">
				  <label
					htmlFor="email"
					className="text-sm font-medium text-white/80"
				  >
					Email
				  </label>

				  <Input
					id="email"
					type="email"
					placeholder="john@example.com"
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
					<p className="text-sm text-red-300">
					  {errors.email.message}
					</p>
				  )}
				</div>

				<div className="space-y-2">
				  <label
					htmlFor="password"
					className="text-sm font-medium text-white/80"
				  >
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
					  aria-label={
						showPassword
						  ? 'Hide password'
						  : 'Show password'
					  }
					  className="
						absolute right-0 top-0 h-full px-3 py-2
						text-white/50
						hover:bg-transparent
						hover:text-white
					  "
					  onClick={() =>
						setShowPassword(!showPassword)
					  }
					>
					  {showPassword ? (
						<EyeOff className="h-4 w-4" />
					  ) : (
						<Eye className="h-4 w-4" />
					  )}
					</Button>
				  </div>

				  {errors.password && (
					<p className="text-sm text-red-300">
					  {errors.password.message}
					</p>
				  )}
				</div>

				<div className="space-y-2">
				  <label
					htmlFor="confirmPassword"
					className="text-sm font-medium text-white/80"
				  >
					Подтвердить пароль
				  </label>

				  <div className="relative">
					<Input
					  id="confirmPassword"
					  type={
						showConfirmPassword ? 'text' : 'password'
					  }
					  placeholder="Подтвердите пароль"
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
					  {...register('confirmPassword')}
					/>

					<Button
					  type="button"
					  variant="ghost"
					  size="icon"
					  aria-label={
						showConfirmPassword
						  ? 'Hide password'
						  : 'Show password'
					  }
					  className="
						absolute right-0 top-0 h-full px-3 py-2
						text-white/50
						hover:bg-transparent
						hover:text-white
					  "
					  onClick={() =>
						setShowConfirmPassword(
						  !showConfirmPassword
						)
					  }
					>
					  {showConfirmPassword ? (
						<EyeOff className="h-4 w-4" />
					  ) : (
						<Eye className="h-4 w-4" />
					  )}
					</Button>
				  </div>

				  {errors.confirmPassword && (
					<p className="text-sm text-red-300">
					  {errors.confirmPassword.message}
					</p>
				  )}
				</div>

				<Button
				  type="submit"
				  disabled={registerMutation.isPending}
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
				>
				  {registerMutation.isPending ? (
					<div className="flex items-center space-x-2">
					  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
					  <span>Создание аккаунта...</span>
					</div>
				  ) : (
					<div className="flex items-center space-x-2">
					  <UserPlus className="h-4 w-4" />
					  <span>Создать аккаунт</span>
					</div>
				  )}
				</Button>
			  </form>

			  <div className="mt-6 text-center text-sm">
				<span className="text-white/50">
				  Уже есть аккаунт?{' '}
				</span>

				<Link
				  to="/login"
				  className="font-medium text-[#1CB4FF] transition-colors hover:text-white"
				>
				  Вход
				</Link>
			  </div>
			</CardContent>
		  </div>
		</Card>
	  </div>
	</div>
  )
}
