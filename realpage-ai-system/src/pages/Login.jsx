import { useState } from 'react';
import { Brain, User, Headphones, ArrowRight, Sparkles, Shield, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import { authAPI } from '../services/api';

export function Login({ onLogin }) {
  const [selectedRole, setSelectedRole] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!selectedRole || !email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await authAPI.login({ email, password }, selectedRole);
      if (response.success) {
        onLogin(response.user);
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Resolution',
      description: 'Intelligent case analysis with automated solution suggestions',
    },
    {
      icon: Shield,
      title: 'Self-Learning System',
      description: 'Continuously improves from agent feedback and approvals',
    },
    {
      icon: Zap,
      title: 'Instant Knowledge Access',
      description: 'RAG-powered search across your entire knowledge base',
    },
  ];

  return (
    <div className="min-h-screen bg-mesh flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        
        {/* Logo */}
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">RealPage AI</h1>
              <p className="text-dark-400">Self-Learning Support System</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="relative z-10 space-y-8">
          <div>
            <h2 className="text-4xl font-bold text-white mb-4 leading-tight">
              Transform Your Support<br />
              <span className="text-gradient">With Intelligent AI</span>
            </h2>
            <p className="text-dark-300 text-lg max-w-md">
              Experience the future of customer support. Our AI learns from every resolution, 
              building an ever-evolving knowledge base that gets smarter with each interaction.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-4">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-dark-800/50 border border-dark-700 flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-primary-400" />
                </div>
                <div>
                  <h3 className="text-white font-medium">{feature.title}</h3>
                  <p className="text-dark-400 text-sm">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">RealPage AI</h1>
              <p className="text-dark-400 text-sm">Self-Learning System</p>
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">Welcome Back</h2>
            <p className="text-dark-400">Sign in to access your portal</p>
          </div>

          {/* Role Selection */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Card
              hover
              glow
              className={`cursor-pointer transition-all duration-300 ${
                selectedRole === 'user'
                  ? 'border-primary-500 bg-primary-500/10'
                  : ''
              }`}
              onClick={() => setSelectedRole('user')}
            >
              <CardContent className="p-4 text-center">
                <div className={`w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center transition-colors ${
                  selectedRole === 'user'
                    ? 'bg-primary-500'
                    : 'bg-dark-700'
                }`}>
                  <User className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-white font-medium">RealPage User</h3>
                <p className="text-dark-400 text-xs mt-1">Submit support cases</p>
              </CardContent>
            </Card>

            <Card
              hover
              glow
              className={`cursor-pointer transition-all duration-300 ${
                selectedRole === 'agent'
                  ? 'border-primary-500 bg-primary-500/10'
                  : ''
              }`}
              onClick={() => setSelectedRole('agent')}
            >
              <CardContent className="p-4 text-center">
                <div className={`w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center transition-colors ${
                  selectedRole === 'agent'
                    ? 'bg-primary-500'
                    : 'bg-dark-700'
                }`}>
                  <Headphones className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-white font-medium">Support Agent</h3>
                <p className="text-dark-400 text-xs mt-1">Resolve & manage cases</p>
              </CardContent>
            </Card>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Email Address
              </label>
              <Input
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Password
              </label>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm">{error}</p>
            )}

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-dark-400">
                <input type="checkbox" className="rounded border-dark-600 bg-dark-800" />
                Remember me
              </label>
              <a href="#" className="text-primary-400 hover:text-primary-300">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              loading={isLoading}
              disabled={!selectedRole}
            >
              Sign In
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </form>

          <p className="text-center text-dark-400 text-sm mt-6">
            Don't have an account?{' '}
            <a href="#" className="text-primary-400 hover:text-primary-300">
              Contact Admin
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
