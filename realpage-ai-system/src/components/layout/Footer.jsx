import { Brain, Github, Linkedin, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-dark-800 bg-dark-950/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">RealPage AI</h3>
                <p className="text-xs text-dark-400">Self-Learning Support System</p>
              </div>
            </div>
            <p className="text-dark-400 text-sm max-w-md mb-4">
              Revolutionizing customer support with AI-powered case resolution. 
              Our self-learning system continuously improves through agent feedback, 
              building an ever-growing knowledge base for faster, more accurate solutions.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-dark-400 hover:text-primary-400 text-sm transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-dark-400 hover:text-primary-400 text-sm transition-colors">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="text-dark-400 hover:text-primary-400 text-sm transition-colors">
                  Knowledge Base
                </a>
              </li>
              <li>
                <a href="#" className="text-dark-400 hover:text-primary-400 text-sm transition-colors">
                  Support Center
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-sm text-dark-400">
              <li>support@realpage-ai.com</li>
              <li>1-800-REALPAGE</li>
              <li>Enterprise Support 24/7</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-dark-800 mt-8 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-dark-500 text-sm">
            © 2026 RealPage AI. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-dark-500 hover:text-dark-300 text-sm transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-dark-500 hover:text-dark-300 text-sm transition-colors">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
