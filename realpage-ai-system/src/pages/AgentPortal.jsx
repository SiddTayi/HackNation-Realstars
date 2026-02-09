import { useState, useEffect } from 'react';
import {
  Search,
  Clock,
  CheckCircle,
  FileText,
  TrendingUp,
  AlertCircle,
  Filter,
  ChevronRight,
  Inbox,
  History,
  Sparkles,
  BookOpen,
  AlertTriangle,
  Eye,
  X,
  ExternalLink,
  Copy,
  LayoutList,
  Calendar,
} from 'lucide-react';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge, PriorityBadge, StatusBadge } from '../components/ui/Badge';
import { caseAPI, knowledgeAPI } from '../services/api';
import { cn, formatDate } from '../lib/utils';

export function AgentPortal({ user, onLogout, onSelectCase }) {
  const [resolvedCases, setResolvedCases] = useState([]);
  const [pendingCases, setPendingCases] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const [activeView, setActiveView] = useState('cases'); // 'cases', 'knowledge', or 'dashboard'
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [showArticleModal, setShowArticleModal] = useState(false);
  
  // Tickets Dashboard state
  const [ticketSearchQuery, setTicketSearchQuery] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  
  // Knowledge articles state
  const [knowledgeArticles, setKnowledgeArticles] = useState([]);

  // Helper to normalize knowledge articles from new_knowledge table
  const normalizeArticle = (article) => ({
    id: article.knowledge_id || article.id,
    title: article.resolution?.substring(0, 80) || 'Untitled',
    product: article.product || 'General',
    category: article.product || 'General',
    createdAt: article.created_at,
    sourceTicket: article.ticket_id || 'N/A',
    content: article.resolution || '',
    conversationId: article.conversation_id,
    ...article,
  });

  const handleViewArticle = (article) => {
    setSelectedArticle(article);
    setShowArticleModal(true);
  };

  const closeArticleModal = () => {
    setShowArticleModal(false);
    setSelectedArticle(null);
  };

  // Calculate SLA status - breach if more than 3 days old
  const getSLAStatus = (createdAt) => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffDays = Math.floor((now - created) / (1000 * 60 * 60 * 24));
    return {
      isBreached: diffDays > 3,
      daysOld: diffDays,
      label: diffDays > 3 ? 'SLA Breach' : 'Within SLA'
    };
  };

  // Demo ticket data for demo mode
  const demoTickets = {
    pending: [
      {
        id: 1,
        caseId: 'CS-99911001',
        issue: 'Date advance failing with validation error - Backend certification reference is invalid',
        category: 'Date Advance',
        product: 'PropertySuite Affordable',
        priority: 'high',
        status: 'pending',
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        transcript: 'Agent: Hi, how can I help you today?\nCustomer: I\'m having trouble with the date advance feature. It keeps failing with a validation error.\nAgent: I understand. Can you tell me what error message you\'re seeing?\nCustomer: It says "Backend certification reference is invalid."',
        aiResolution: 'This issue requires running a backend data correction script to fix the invalid certification reference. Apply SCRIPT-0121 to resolve the validation mismatch.',
        relevancyScore: 0.92,
      },
      {
        id: 2,
        caseId: 'CS-99911002',
        issue: 'Bulk rent collection timing out for large property with 250+ units',
        category: 'Payments',
        product: 'PropertySuite Accounting',
        priority: 'medium',
        status: 'pending',
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        transcript: 'Customer: The bulk rent collection is timing out for our large property.\nAgent: How many units are in this property?\nCustomer: About 250 units.\nAgent: I see. Large batch operations can hit timeout limits.',
        aiResolution: 'Increase the payment gateway timeout to 120 seconds and implement batch processing with 25 units per batch. Reference KB-SYN-0127 for detailed steps.',
        relevancyScore: 0.88,
      },
      {
        id: 3,
        caseId: 'CS-99911003',
        issue: 'Certification renewal failing - State portal sync error',
        category: 'Certifications',
        product: 'PropertySuite Affordable',
        priority: 'high',
        status: 'pending',
        createdAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        transcript: 'Subject: Certification renewal failing\n\nHi Support,\n\nWe are unable to complete the annual certification renewal for several residents. The system shows a sync error with the state portal.',
        aiResolution: 'State portal sync errors typically occur due to SSN format mismatches. Verify SSN format before submission and use the batch upload feature. See KB-SYN-0126.',
        relevancyScore: 0.85,
      },
    ],
    resolved: [
      {
        id: 4,
        caseId: 'CS-99910001',
        issue: 'Users getting logged out randomly - Token expiry issue',
        category: 'Authentication',
        product: 'PropertySuite Core',
        priority: 'medium',
        status: 'approved',
        createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        resolvedAt: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
        transcript: 'Customer: Users are getting logged out randomly.\nAgent: This is related to token expiry. We\'ve extended the session timeout and the issue should be resolved now.',
        aiResolution: 'Extended JWT token expiry from 30 minutes to 8 hours for improved user experience.',
        relevancyScore: 0.95,
      },
      {
        id: 5,
        caseId: 'CS-99910002',
        issue: 'Lease renewal notifications not being sent',
        category: 'Leasing',
        product: 'PropertySuite Leasing',
        priority: 'low',
        status: 'approved',
        createdAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
        resolvedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        transcript: 'Customer: Lease renewal notifications are not being sent.\nAgent: I\'ve enabled the notification settings and configured the 60-day reminder.',
        aiResolution: 'Enabled lease expiration alerts with 60-day notification timeline. See KB-SYN-0122 for setup guide.',
        relevancyScore: 0.91,
      },
    ],
  };

  useEffect(() => {
    loadCases();
    loadKnowledgeArticles();
  }, []);

  const loadKnowledgeArticles = async () => {
    try {
      const response = await knowledgeAPI.getArticles();
      if (response.articles) {
        setKnowledgeArticles(response.articles.map(normalizeArticle));
      }
    } catch (error) {
      console.error('Error loading knowledge articles:', error);
    }
  };

  // Helper to normalize backend data (snake_case) to frontend format (camelCase)
  const normalizeCase = (c) => ({
    caseId: c.ticket_id || c.caseId,
    issue: c.issue_summary || c.transcript?.substring(0, 100) || c.issue || 'No description',
    category: c.category || c.product || 'General',
    priority: c.priority || 'Medium',
    status: c.status,
    createdAt: c.created_at || c.createdAt,
    resolvedAt: c.resolved_at || c.resolvedAt,
    transcript: c.transcript,
    aiResolution: c.ai_resolution || c.original_resolution || c.aiResolution,
    relevancyScore: c.relevancy_score || c.relevancyScore,
    tier: c.tier,
    assignedTo: c.assigned_to,
    // Keep original data for detail view
    ...c,
  });

  const loadCases = async () => {
    setIsLoading(true);
    try {
      // Use demo data if in demo mode
      if (user?.isDemo) {
        setPendingCases(demoTickets.pending);
        setResolvedCases(demoTickets.resolved);
        setIsLoading(false);
        return;
      }

      const [resolvedRes, pendingRes] = await Promise.all([
        caseAPI.getResolvedCases(user.id),
        caseAPI.getPendingCases(user.id),
      ]);
      // Normalize backend data to frontend format
      setResolvedCases((resolvedRes.cases || []).map(normalizeCase));
      setPendingCases((pendingRes.cases || []).map(normalizeCase));
    } catch (error) {
      console.error('Error loading cases:', error);
      // Fallback to demo data on error
      if (user?.isDemo) {
        setPendingCases(demoTickets.pending);
        setResolvedCases(demoTickets.resolved);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await caseAPI.searchCases(searchQuery);
      setSearchResults(response.results);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const filteredPendingCases = pendingCases.filter((c) => {
    if (activeFilter === 'all') return true;
    const sla = getSLAStatus(c.createdAt);
    if (activeFilter === 'breach') return sla.isBreached;
    if (activeFilter === 'within') return !sla.isBreached;
    return true;
  });

  // Count SLA breaches
  const slaBreachCount = pendingCases.filter(c => getSLAStatus(c.createdAt).isBreached).length;

  const stats = [
    {
      label: 'Pending Tickets',
      value: pendingCases.length,
      icon: Clock,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/20',
    },
    {
      label: 'Resolved Today',
      value: resolvedCases.filter(
        (c) => new Date(c.resolvedAt).toDateString() === new Date().toDateString()
      ).length,
      icon: CheckCircle,
      color: 'text-accent-400',
      bg: 'bg-accent-500/20',
    },
    {
      label: 'Total Resolved',
      value: resolvedCases.length,
      icon: TrendingUp,
      color: 'text-primary-400',
      bg: 'bg-primary-500/20',
    },
    {
      label: 'SLA Breach',
      value: slaBreachCount,
      icon: AlertTriangle,
      color: 'text-red-400',
      bg: 'bg-red-500/20',
    },
  ];

  return (
    <div className="min-h-screen bg-mesh flex flex-col">
      <Header user={user} onLogout={onLogout} />

      <main className="flex-1 pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user.name}
            </h1>
            <p className="text-dark-400">
              Manage and resolve support cases with AI-powered assistance
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {stats.map((stat, index) => (
              <Card key={index} className="hover:border-dark-600 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-dark-400 text-sm">{stat.label}</p>
                      <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                    </div>
                    <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', stat.bg)}>
                      <stat.icon className={cn('w-5 h-5', stat.color)} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Navigation Tabs */}
          <div className="flex gap-4 mb-6 border-b border-dark-700">
            <button
              onClick={() => setActiveView('cases')}
              className={cn(
                'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
                activeView === 'cases'
                  ? 'text-primary-400 border-primary-500'
                  : 'text-dark-400 border-transparent hover:text-white'
              )}
            >
              <Inbox className="w-4 h-4" />
              Ticket Management
            </button>
            <button
              onClick={() => setActiveView('dashboard')}
              className={cn(
                'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
                activeView === 'dashboard'
                  ? 'text-primary-400 border-primary-500'
                  : 'text-dark-400 border-transparent hover:text-white'
              )}
            >
              <LayoutList className="w-4 h-4" />
              Tickets Dashboard
            </button>
            <button
              onClick={() => setActiveView('knowledge')}
              className={cn(
                'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
                activeView === 'knowledge'
                  ? 'text-primary-400 border-primary-500'
                  : 'text-dark-400 border-transparent hover:text-white'
              )}
            >
              <BookOpen className="w-4 h-4" />
              Knowledge Articles
            </button>
          </div>

          {activeView === 'cases' && (
          /* Main Three-Panel Layout */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Panel - Resolved Tickets (1/3) */}
            <div className="lg:col-span-3">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <History className="w-5 h-5 text-accent-400" />
                    <h2 className="text-lg font-semibold text-white">Resolved Tickets</h2>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden p-0">
                  <div className="h-full overflow-y-auto scrollbar-thin px-4 pb-4">
                    {resolvedCases.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <div className="w-12 h-12 rounded-full bg-dark-700 flex items-center justify-center mb-3">
                          <FileText className="w-6 h-6 text-dark-500" />
                        </div>
                        <p className="text-dark-400 text-sm">No resolved tickets yet</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {resolvedCases.map((caseItem) => (
                          <div
                            key={caseItem.caseId}
                            className="bg-dark-700/50 rounded-lg p-3 border border-dark-600 hover:border-dark-500 transition-colors cursor-pointer"
                          >
                            <p className="text-xs text-dark-400 font-mono mb-1">
                              {caseItem.caseId}
                            </p>
                            <p className="text-white text-sm font-medium line-clamp-2">
                              {caseItem.issue}
                            </p>
                            <div className="flex items-center justify-between mt-2">
                              <StatusBadge status={caseItem.status} />
                              <span className="text-xs text-dark-500">
                                {formatDate(caseItem.resolvedAt)}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Middle Panel - Search (2/3) */}
            <div className="lg:col-span-5">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="flex-shrink-0">
                  <div className="flex items-center gap-2 mb-4">
                    <Search className="w-5 h-5 text-primary-400" />
                    <h2 className="text-lg font-semibold text-white">Knowledge Search</h2>
                    <Badge variant="primary" className="ml-auto">
                      <Sparkles className="w-3 h-3 mr-1" />
                      RAG Powered
                    </Badge>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Search tickets, resolutions, or knowledge base..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1"
                    />
                    <Button onClick={handleSearch} loading={isSearching}>
                      <Search className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden p-0">
                  <div className="h-full overflow-y-auto scrollbar-thin px-4 pb-4">
                    {searchResults.length === 0 && !searchQuery ? (
                      <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <div className="w-16 h-16 rounded-full bg-primary-500/10 flex items-center justify-center mb-4">
                          <Search className="w-8 h-8 text-primary-400" />
                        </div>
                        <h3 className="text-white font-medium mb-2">Search Knowledge Base</h3>
                        <p className="text-dark-400 text-sm max-w-xs">
                          Use RAG-powered search to find similar cases and resolutions from the knowledge base
                        </p>
                        <div className="flex flex-wrap gap-2 mt-4 justify-center">
                          {['authentication issues', 'payment errors', 'API timeout'].map((query) => (
                            <button
                              key={query}
                              onClick={() => setSearchQuery(query)}
                              className="text-xs px-3 py-1.5 rounded-full bg-dark-700 text-dark-300 hover:bg-dark-600 hover:text-white transition-colors"
                            >
                              {query}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : searchResults.length === 0 && searchQuery ? (
                      <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <p className="text-dark-400">No results found for "{searchQuery}"</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <p className="text-dark-400 text-sm">
                          Found {searchResults.length} related results
                        </p>
                        {searchResults.map((result, index) => (
                          <div
                            key={index}
                            className="bg-dark-700/50 rounded-lg p-4 border border-dark-600"
                          >
                            <div className="flex items-start justify-between gap-4 mb-2">
                              <p className="text-xs text-primary-400 font-mono">
                                {result.caseId}
                              </p>
                              <Badge variant="success">
                                {Math.round(result.relevanceScore * 100)}% match
                              </Badge>
                            </div>
                            <p className="text-white font-medium mb-2">{result.issue}</p>
                            <p className="text-dark-300 text-sm">{result.resolution}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Panel - Tickets to Resolve (1/3) */}
            <div className="lg:col-span-4">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="flex-shrink-0">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Inbox className="w-5 h-5 text-yellow-400" />
                      <h2 className="text-lg font-semibold text-white">Tickets to Resolve</h2>
                    </div>
                    <Badge variant="warning">{pendingCases.length} pending</Badge>
                  </div>
                  
                  {/* SLA-based Filters */}
                  <div className="flex gap-2">
                    {[
                      { key: 'all', label: 'All' },
                      { key: 'breach', label: 'SLA Breach', color: 'bg-red-500' },
                      { key: 'within', label: 'Within SLA', color: 'bg-green-500' },
                    ].map((filter) => (
                      <button
                        key={filter.key}
                        onClick={() => setActiveFilter(filter.key)}
                        className={cn(
                          'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                          activeFilter === filter.key
                            ? filter.color || 'bg-primary-500' + ' text-white'
                            : 'bg-dark-700 text-dark-300 hover:bg-dark-600',
                          activeFilter === filter.key && 'text-white'
                        )}
                      >
                        {filter.label}
                      </button>
                    ))}
                  </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden p-0">
                  <div className="h-full overflow-y-auto scrollbar-thin px-4 pb-4">
                    {isLoading ? (
                      <div className="flex items-center justify-center h-full">
                        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full" />
                      </div>
                    ) : filteredPendingCases.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <div className="w-12 h-12 rounded-full bg-accent-500/10 flex items-center justify-center mb-3">
                          <CheckCircle className="w-6 h-6 text-accent-400" />
                        </div>
                        <p className="text-dark-400 text-sm">No pending tickets</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {filteredPendingCases.map((caseItem) => (
                          <div
                            key={caseItem.ticket_id}
                            onClick={() => onSelectCase(caseItem)}
                            className="bg-dark-700/50 rounded-lg p-4 border border-dark-600 hover:border-primary-500/50 hover:bg-dark-700/80 transition-all cursor-pointer group"
                          >
                            {(() => {
                              const sla = getSLAStatus(caseItem.createdAt);
                              return (
                                <>
                                  <div className="flex items-start justify-between gap-2 mb-2">
                                    <p className="text-xs text-primary-400 font-mono">
                                      {caseItem.ticket_id}
                                    </p>
                                    {sla.isBreached ? (
                                      <Badge variant="danger" className="text-xs">
                                        <AlertTriangle className="w-3 h-3 mr-1" />
                                        SLA Breach
                                      </Badge>
                                    ) : (
                                      <Badge variant="success" className="text-xs">
                                        Within SLA
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-white font-medium mb-2 line-clamp-2">
                                    {caseItem.issue}
                                  </p>
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                      <Badge variant="info">{caseItem.category}</Badge>
                                    </div>
                                    <ChevronRight className="w-4 h-4 text-dark-500 group-hover:text-primary-400 transition-colors" />
                                  </div>
                                  <p className={cn(
                                    "text-xs mt-2",
                                    sla.isBreached ? "text-red-400" : "text-dark-500"
                                  )}>
                                    Submitted {formatDate(caseItem.createdAt)}
                                    {sla.isBreached && ` (${sla.daysOld} days ago)`}
                                  </p>
                                </>
                              );
                            })()}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
          )}

          {activeView === 'knowledge' && (
          /* Knowledge Articles Dashboard */
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-primary-400" />
                  <h2 className="text-lg font-semibold text-white">New Knowledge Articles</h2>
                </div>
                <Badge variant="primary">
                  <Sparkles className="w-3 h-3 mr-1" />
                  AI Generated
                </Badge>
              </div>
              <p className="text-dark-400 text-sm mt-2">
                Recently added knowledge base articles from approved resolutions
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {knowledgeArticles.map((article) => (
                  <div
                    key={article.id}
                    className="bg-dark-700/50 rounded-lg p-4 border border-dark-600 hover:border-primary-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <Badge variant="primary" className="text-xs">
                        {article.knowledge_id}
                      </Badge>
                    </div>
                    <h3 className="text-white font-medium mb-2 line-clamp-2">
                      {article.resolution?.substring(0, 80) || 'No resolution'}
                    </h3>
                    <div className="flex flex-wrap gap-2 mb-3">
                      <Badge variant="info" className="text-xs">{article.product || 'General'}</Badge>
                    </div>
                    <div className="flex items-center justify-between text-xs mb-3">
                      <span className="text-dark-400">
                        From: <span className="text-primary-400 font-mono">{article.ticket_id || 'N/A'}</span>
                      </span>
                      <span className="text-dark-500">
                        {formatDate(article.created_at)}
                      </span>
                    </div>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="w-full"
                      onClick={() => handleViewArticle(article)}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Article
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          )}

          {activeView === 'dashboard' && (
          /* Tickets Dashboard */
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <LayoutList className="w-5 h-5 text-primary-400" />
                  <h2 className="text-lg font-semibold text-white">All Tickets</h2>
                </div>
                <Badge variant="info">
                  {[...pendingCases, ...resolvedCases].length} Total
                </Badge>
              </div>
              
              {/* Search and Filters */}
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                    <input
                      type="text"
                      placeholder="Search by ticket ID, issue, or category..."
                      value={ticketSearchQuery}
                      onChange={(e) => setTicketSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-primary-500"
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-dark-400" />
                  <input
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  />
                  <span className="text-dark-400">to</span>
                  <input
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  />
                  {(dateFrom || dateTo) && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => { setDateFrom(''); setDateTo(''); }}
                    >
                      Clear
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Tickets Table */}
              <div className="overflow-x-auto overflow-y-scroll h-[calc(100vh-20rem)]">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-dark-700">
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Ticket ID</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Issue</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Category</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Status</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">SLA</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Created</th>
                      <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...pendingCases, ...resolvedCases]
                      .filter(ticket => {
                        // Search filter
                        if (ticketSearchQuery) {
                          const query = ticketSearchQuery.toLowerCase();
                          return (
                            ticket.caseId?.toLowerCase().includes(query) ||
                            ticket.issue?.toLowerCase().includes(query) ||
                            ticket.category?.toLowerCase().includes(query)
                          );
                        }
                        return true;
                      })
                      .filter(ticket => {
                        // Date range filter
                        if (dateFrom || dateTo) {
                          const ticketDate = new Date(ticket.createdAt || ticket.resolvedAt);
                          if (dateFrom && ticketDate < new Date(dateFrom)) return false;
                          if (dateTo && ticketDate > new Date(dateTo + 'T23:59:59')) return false;
                        }
                        return true;
                      })
                      .map((ticket) => {
                        const ticketDate = ticket.createdAt || ticket.resolvedAt;
                        const sla = getSLAStatus(ticketDate);
                        return (
                          <tr
                            key={ticket.caseId}
                            className="border-b border-dark-700/50 hover:bg-dark-700/30 transition-colors"
                          >
                            <td className="py-3 px-4">
                              <span className="text-primary-400 font-mono text-sm">{ticket.caseId}</span>
                            </td>
                            <td className="py-3 px-4">
                              <p className="text-white text-sm line-clamp-1 max-w-xs">{ticket.issue}</p>
                            </td>
                            <td className="py-3 px-4">
                              <Badge variant="info" className="text-xs">{ticket.category || 'General'}</Badge>
                            </td>
                            <td className="py-3 px-4">
                              <StatusBadge status={ticket.status} />
                            </td>
                            <td className="py-3 px-4">
                              {ticket.status === 'pending' ? (
                                sla.isBreached ? (
                                  <Badge variant="danger" className="text-xs">
                                    <AlertTriangle className="w-3 h-3 mr-1" />
                                    Breach ({sla.daysOld}d)
                                  </Badge>
                                ) : (
                                  <Badge variant="success" className="text-xs">
                                    Within SLA
                                  </Badge>
                                )
                              ) : (
                                <span className="text-dark-500 text-xs">Resolved</span>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              <span className="text-dark-400 text-sm">{formatDate(ticketDate)}</span>
                            </td>
                            <td className="py-3 px-4">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onSelectCase(ticket)}
                              >
                                <Eye className="w-4 h-4 mr-1" />
                                View
                              </Button>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
                
                {[...pendingCases, ...resolvedCases].length === 0 && (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 text-dark-500 mx-auto mb-4" />
                    <p className="text-dark-400">No tickets found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          )}
        </div>
      </main>

      {/* Knowledge Article Modal */}
      {showArticleModal && selectedArticle && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-800 rounded-xl border border-dark-700 w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-700">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="primary">{selectedArticle.id}</Badge>
                  <Badge variant="info">{selectedArticle.category}</Badge>
                </div>
                <h2 className="text-xl font-semibold text-white mb-2">
                  {selectedArticle.title}
                </h2>
                <div className="flex items-center gap-4 text-sm text-dark-400">
                  <span>Product: <span className="text-white">{selectedArticle.product}</span></span>
                  <span>Source: <span className="text-primary-400 font-mono">{selectedArticle.sourceTicket}</span></span>
                </div>
              </div>
              <button
                onClick={closeArticleModal}
                className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="prose prose-invert max-w-none">
                <div className="bg-dark-700/50 rounded-lg p-4 mb-4">
                  <h4 className="text-sm font-medium text-dark-400 mb-2">Reference Articles</h4>
                  <div className="flex gap-2">
                    <Badge variant="secondary">
                      <FileText className="w-3 h-3 mr-1" />
                      {selectedArticle.referenceKb}
                    </Badge>
                    <Badge variant="secondary">
                      <FileText className="w-3 h-3 mr-1" />
                      {selectedArticle.referenceScript}
                    </Badge>
                  </div>
                </div>
                
                <div className="text-dark-200 whitespace-pre-wrap">
                  {selectedArticle.content.split('\n').map((line, i) => {
                    if (line.startsWith('## ')) {
                      return <h3 key={i} className="text-lg font-semibold text-white mt-6 mb-3">{line.replace('## ', '')}</h3>;
                    }
                    if (line.startsWith('```')) {
                      return null;
                    }
                    if (line.startsWith('- ')) {
                      return <li key={i} className="ml-4 text-dark-300">{line.replace('- ', '')}</li>;
                    }
                    if (line.match(/^\d+\./)) {
                      return <li key={i} className="ml-4 text-dark-300 list-decimal">{line.replace(/^\d+\.\s*/, '')}</li>;
                    }
                    return <p key={i} className="text-dark-300 mb-2">{line}</p>;
                  })}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-700 bg-dark-800/50">
              <div className="flex items-center gap-4 text-sm text-dark-400">
                <span>{selectedArticle.views} views</span>
                <span>Created {formatDate(selectedArticle.createdAt)}</span>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm">
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Content
                </Button>
                <Button variant="secondary" size="sm">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open in KB
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}

export default AgentPortal;
