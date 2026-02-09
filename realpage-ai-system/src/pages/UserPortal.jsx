import { useState } from 'react';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  Clock,
  ArrowRight,
  Sparkles,
  Database,
  Brain,
  Zap,
  Shield,
  Users,
  Download,
  Eye,
  X,
  AlertCircle,
} from 'lucide-react';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { FileUpload } from '../components/ui/FileUpload';
import { Badge, PriorityBadge } from '../components/ui/Badge';
import { caseAPI } from '../services/api';
import { cn } from '../lib/utils';

// Demo tickets for demo mode
const demoSubmittedTickets = [
  {
    id: 1,
    ticket_id: 'CS-99911001',
    conversation_id: 'CONV-2024-001',
    channel: 'Chat',
    customer_role: 'Property Manager',
    product: 'PropertySuite Affordable',
    transcript: 'Agent: Hi, how can I help you today?\nCustomer: I\'m having trouble with the date advance feature. It keeps failing with a validation error.\nAgent: I understand. Can you tell me what error message you\'re seeing?\nCustomer: It says "Backend certification reference is invalid."\nAgent: Let me check that for you.',
    status: 'pending',
    priority: 'high',
    category: 'Date Advance',
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    ai_resolution: 'This issue requires running a backend data correction script to fix the invalid certification reference.',
    relevancy_score: 0.92,
  },
  {
    id: 2,
    ticket_id: 'CS-99911002',
    conversation_id: 'CONV-2024-002',
    channel: 'Phone',
    customer_role: 'Accountant',
    product: 'PropertySuite Accounting',
    transcript: 'Customer: The bulk rent collection is timing out.\nAgent: How many units?\nCustomer: About 250 units.\nAgent: Large batch operations can hit timeout limits.',
    status: 'pending',
    priority: 'medium',
    category: 'Payments',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    ai_resolution: 'Increase payment gateway timeout to 120 seconds and implement batch processing.',
    relevancy_score: 0.88,
  },
  {
    id: 3,
    ticket_id: 'CS-99911003',
    conversation_id: 'CONV-2024-003',
    channel: 'Email',
    customer_role: 'Compliance Officer',
    product: 'PropertySuite Affordable',
    transcript: 'Subject: Certification renewal failing\n\nWe are unable to complete the annual certification renewal. The system shows a sync error with the state portal.',
    status: 'approved',
    priority: 'high',
    category: 'Certifications',
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    ai_resolution: 'State portal sync errors occur due to SSN format mismatches. Verify SSN format before submission.',
    relevancy_score: 0.85,
  },
];

export function UserPortal({ user, onLogout }) {
  const [currentStep, setCurrentStep] = useState(user?.isDemo ? 3 : 1);
  const [selectedFile, setSelectedFile] = useState(null);
  const [parsedTickets, setParsedTickets] = useState([]);
  const [submittedTickets, setSubmittedTickets] = useState(user?.isDemo ? demoSubmittedTickets : []);
  const [aiProcessing, setAiProcessing] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [parseError, setParseError] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Check if all tickets are valid
  const hasInvalidTickets = parsedTickets.some(t => !t.isValid);
  const validTicketsCount = parsedTickets.filter(t => t.isValid).length;
  const invalidTicketsCount = parsedTickets.filter(t => !t.isValid).length;

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setParsedTickets([]);
    setParseError('');
  };

  const handleParseFile = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setParseError('');
    try {
      const response = await caseAPI.uploadFile(selectedFile);
      if (response.success) {
        setParsedTickets(response.parsedData);
        setCurrentStep(2);
      } else {
        setParseError(response.error || 'Failed to parse file');
      }
    } catch (error) {
      console.error('Error parsing file:', error);
      setParseError('An unexpected error occurred while parsing the file');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleViewTicket = (ticketItem) => {
    setSelectedCase(ticketItem);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedCase(null);
  };

  const handleSubmitTickets = async () => {
    if (parsedTickets.length === 0) return;

    setIsSubmitting(true);
    try {
      const response = await caseAPI.submitTickets(parsedTickets);
      if (response.success) {
        setSubmittedTickets(response.tickets || []);
        setAiProcessing(response.ai_processing || []);
        setCurrentStep(3);
      }
    } catch (error) {
      console.error('Error submitting tickets:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Our system analyzes your cases using advanced NLP to understand the issue context',
    },
    {
      icon: Database,
      title: 'Knowledge Matching',
      description: 'RAG search finds similar resolved cases from our extensive knowledge base',
    },
    {
      icon: Zap,
      title: 'Instant Resolution',
      description: 'Get AI-generated solutions within seconds of case submission',
    },
    {
      icon: Users,
      title: 'Expert Assignment',
      description: 'Cases are automatically routed to the most qualified support agents',
    },
  ];

  const steps = [
    { number: 1, title: 'Upload File', description: 'Upload your Excel file' },
    { number: 2, title: 'Review Cases', description: 'Verify parsed data' },
    { number: 3, title: 'Submitted', description: 'Cases assigned' },
  ];

  return (
    <div className="min-h-screen bg-mesh flex flex-col">
      <Header user={user} onLogout={onLogout} />

      <main className="flex-1 pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <Badge variant="primary" className="mb-4">
              <Sparkles className="w-3 h-3 mr-1" />
              Self-Learning AI System
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              RealPage Self-Learning<br />
              <span className="text-gradient">AI Support System</span>
            </h1>
            <p className="text-dark-300 text-lg max-w-2xl mx-auto">
              Upload your support cases and let our AI analyze, categorize, and generate 
              intelligent resolutions. Every approved solution makes our system smarter.
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-12">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all',
                      currentStep >= step.number
                        ? 'bg-primary-500 text-white'
                        : 'bg-dark-700 text-dark-400'
                    )}
                  >
                    {currentStep > step.number ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      step.number
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <p className={cn(
                      'text-sm font-medium',
                      currentStep >= step.number ? 'text-white' : 'text-dark-400'
                    )}>
                      {step.title}
                    </p>
                    <p className="text-xs text-dark-500 hidden sm:block">{step.description}</p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      'w-20 sm:w-32 h-0.5 mx-4 transition-colors',
                      currentStep > step.number ? 'bg-primary-500' : 'bg-dark-700'
                    )}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Main Content Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Upload Section */}
            <div className="lg:col-span-2">
              <Card className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-primary-900/50 to-cyan-900/50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center">
                      {currentStep === 3 ? (
                        <CheckCircle className="w-5 h-5 text-accent-400" />
                      ) : (
                        <FileSpreadsheet className="w-5 h-5 text-primary-400" />
                      )}
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-white">
                        {currentStep === 1 && 'Upload File'}
                        {currentStep === 2 && 'Review Parsed Cases'}
                        {currentStep === 3 && 'Cases Successfully Submitted'}
                      </h2>
                      <p className="text-dark-400 text-sm">
                        {currentStep === 1 && 'Upload an Excel file containing your Conversation of the issues. Download the template from here.'}
                        {currentStep === 2 && 'Verify the parsed data before submission'}
                        {currentStep === 3 && 'Your cases have been assigned to agents'}
                      </p>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="p-6">
                  {currentStep === 1 && (
                    <div className="space-y-6">
                      <FileUpload onFileSelect={handleFileSelect} />
                      
                      <div className="flex items-center justify-center">
                        <a
                          href="/Sample_Conversation_Info.xlsx"
                          download="Sample_Conversation_Info.xlsx"
                          className="inline-flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          Download Template Excel File
                        </a>
                      </div>

                      {/* Pro Tip */}
                      <div className="bg-gradient-to-br from-primary-900/30 to-cyan-900/30 border border-primary-500/30 rounded-xl p-4">
                        <div className="flex items-center gap-3 mb-2">
                          <Sparkles className="w-5 h-5 text-primary-400" />
                          <h3 className="text-white font-semibold">Pro Tip</h3>
                        </div>
                        <p className="text-dark-300 text-sm">
                          For best results, ensure your Excel file has columns for&nbsp; 
                          <span className="text-primary-400">all the required fields.</span><br/>
                          <span className='text-cyan-200'>Refer to the template for the correct column names.</span>
                          
                        </p>
                      </div>

                      {selectedFile && (
                        <div className="flex justify-end">
                          <Button onClick={handleParseFile} loading={isProcessing}>
                            Parse File
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      )}

                      {parseError && (
                        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="text-red-400 font-medium">Error Parsing File</p>
                            <p className="text-red-300 text-sm">{parseError}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {currentStep === 2 && (
                    <div className="space-y-4">
                      <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-700">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-white font-medium">
                            Parsed Conversations ({parsedTickets.length})
                          </h3>
                          <div className="flex items-center gap-2">
                            {invalidTicketsCount > 0 && (
                              <Badge variant="danger">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                {invalidTicketsCount} Invalid
                              </Badge>
                            )}
                            {validTicketsCount > 0 && (
                              <Badge variant="success">{validTicketsCount} Valid</Badge>
                            )}
                          </div>
                        </div>

                        {/* Table Header */}
                        <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-dark-700/50 rounded-lg mb-2 text-xs font-medium text-dark-300">
                          <div className="col-span-3">Conversation ID</div>
                          <div className="col-span-3">Channel</div>
                          <div className="col-span-3">Customer Role</div>
                          <div className="col-span-2">Status</div>
                          <div className="col-span-1 text-center">Action</div>
                        </div>
                        
                        <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
                          {parsedTickets.map((ticketItem, index) => (
                            <div
                              key={index}
                              className={cn(
                                "grid grid-cols-12 gap-2 items-center px-4 py-3 rounded-lg transition-colors",
                                ticketItem.isValid 
                                  ? "bg-dark-700/50 border border-dark-600 hover:bg-dark-700" 
                                  : "bg-red-500/10 border-2 border-red-500/50 hover:bg-red-500/20"
                              )}
                            >
                              <div className="col-span-3">
                                <p className={cn(
                                  "text-sm font-mono truncate",
                                  ticketItem.conversationId ? "text-white" : "text-red-400 italic"
                                )}>
                                  {ticketItem.conversationId || 'Missing'}
                                </p>
                              </div>
                              <div className="col-span-3">
                                <Badge variant={ticketItem.channel ? "info" : "danger"} className="text-xs">
                                  {ticketItem.channel || 'Missing'}
                                </Badge>
                              </div>
                              <div className="col-span-3">
                                <p className={cn(
                                  "text-sm truncate",
                                  ticketItem.customerRole ? "text-dark-300" : "text-red-400 italic"
                                )}>
                                  {ticketItem.customerRole || 'Missing'}
                                </p>
                              </div>
                              <div className="col-span-2">
                                {ticketItem.isValid ? (
                                  <Badge variant="success" className="text-xs">
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    Valid
                                  </Badge>
                                ) : (
                                  <Badge variant="danger" className="text-xs">
                                    <AlertCircle className="w-3 h-3 mr-1" />
                                    {ticketItem.missingFields?.length} Missing
                                  </Badge>
                                )}
                              </div>
                              <div className="col-span-1 text-center">
                                <button
                                  onClick={() => handleViewTicket(ticketItem)}
                                  className="p-1.5 rounded-lg bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 transition-colors"
                                  title="View Details"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {hasInvalidTickets && (
                        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="text-red-400 font-medium">Cannot Submit</p>
                            <p className="text-red-300 text-sm">
                              {invalidTicketsCount} row(s) have missing required fields. Please fix the data in your Excel file and re-upload.
                            </p>
                          </div>
                        </div>
                      )}

                      <div className="flex justify-between">
                        <Button variant="secondary" onClick={() => setCurrentStep(1)}>
                          Back
                        </Button>
                        <Button 
                          onClick={handleSubmitTickets} 
                          loading={isSubmitting}
                          disabled={hasInvalidTickets || parsedTickets.length === 0}
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          Submit Tickets ({validTicketsCount})
                        </Button>
                      </div>
                    </div>
                  )}

                  {currentStep === 3 && (
                    <div className="space-y-4">
                      <div className="text-center py-6">
                        <div className="w-16 h-16 rounded-full bg-accent-500/20 flex items-center justify-center mx-auto mb-4">
                          <CheckCircle className="w-8 h-8 text-accent-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-2">
                          Cases Submitted Successfully!
                        </h3>
                        <p className="text-dark-400">
                          AI resolutions have been generated and agents have been assigned.
                        </p>
                      </div>

                      <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-thin">
                        {submittedTickets.map((ticketItem) => {
                          // Find matching AI processing data for this ticket
                          const aiData = aiProcessing.find(ai => ai.ticket_id === ticketItem.ticket_id);
                          const agentId = aiData?.classification?.RAG_response?.resolution?.agent_id || 'N/A';
                          const tier = aiData?.classification?.RAG_response?.resolution?.tier || 'N/A';
                          const relevancyScore = ticketItem.relevancy_score || aiData?.classification?.RAG_response?.resolution?.relevancy_score || 0;
                          
                          return (
                            <div
                              key={ticketItem.ticket_id || ticketItem.id}
                              className="bg-dark-700/50 rounded-lg p-4 border border-dark-600"
                            >
                              <div className="flex items-start justify-between gap-4 mb-3">
                                <div>
                                  <p className="text-xs text-primary-400 font-mono mb-1">
                                    {ticketItem.ticket_id}
                                  </p>
                                  <p className="text-white font-medium">{ticketItem.conversation_id}</p>
                                </div>
                                <Badge variant={ticketItem.status === 'pending' ? 'warning' : 'success'}>
                                  <Clock className="w-3 h-3 mr-1" />
                                  {ticketItem.status || 'Pending'}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 text-sm flex-wrap">
                                <span className="text-dark-400">
                                  Assigned: <span className="text-primary-400 font-medium">{agentId}</span>
                                </span>
                                <span className="text-dark-400">
                                  Tier: <span className="text-white">{tier}</span>
                                </span>
                                <span className="text-dark-400">
                                  Relevancy: <span className="text-accent-400">{relevancyScore}%</span>
                                </span>
                              </div>
                              {ticketItem.ai_resolution && (
                                <div className="mt-3 pt-3 border-t border-dark-600">
                                  <p className="text-xs text-dark-400 mb-1">AI Resolution:</p>
                                  <p className="text-sm text-dark-300 line-clamp-2">{ticketItem.ai_resolution}</p>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      <div className="flex justify-center pt-4">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setCurrentStep(1);
                            setSelectedFile(null);
                            setParsedTickets([]);
                            setSubmittedTickets([]);
                            setAiProcessing([]);
                          }}
                        >
                          Submit More Tickets
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Info Sidebar */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Shield className="w-5 h-5 text-primary-400" />
                    How It Works
                  </h3>
                </CardHeader>
                <CardContent className="space-y-4">
                  {features.map((feature, index) => (
                    <div key={index} className="flex gap-3">
                      <div className="w-8 h-8 rounded-lg bg-dark-700 flex items-center justify-center flex-shrink-0">
                        <feature.icon className="w-4 h-4 text-primary-400" />
                      </div>
                      <div>
                        <h4 className="text-white text-sm font-medium">{feature.title}</h4>
                        <p className="text-dark-400 text-xs">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      {/* Case Detail Modal */}
      {showModal && selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={closeModal}
          />
          
          {/* Modal Content */}
          <div className="relative bg-dark-800 rounded-2xl border border-dark-600 w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-dark-700 bg-gradient-to-r from-primary-900/50 to-cyan-900/50">
              <div>
                <h3 className="text-lg font-semibold text-white">Conversation Details</h3>
                <p className="text-dark-400 text-sm">ID: {selectedCase.conversationId || 'N/A'}</p>
              </div>
              <button
                onClick={closeModal}
                className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              {/* Validation Status */}
              {!selectedCase.isValid && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-2 text-red-400 font-medium mb-2">
                    <AlertCircle className="w-4 h-4" />
                    Missing Required Fields
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedCase.missingFields?.map((field, idx) => (
                      <Badge key={idx} variant="danger" className="text-xs">{field}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Conversation ID</label>
                  <p className={cn(
                    "text-sm font-mono p-2 rounded-lg bg-dark-700/50",
                    selectedCase.conversationId ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.conversationId || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Channel</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.channel ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.channel || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Created Date</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.createdDate ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.createdDate || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Customer Role</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.customerRole ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.customerRole || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Agent Name</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.agentName ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.agentName || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Product</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.product ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.product || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Account Name</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.accountName ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.accountName || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Property Name</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.propertyName ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.propertyName || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Property City</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.propertyCity ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.propertyCity || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Property State</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.propertyState ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.propertyState || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Contact Name</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.contactName ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.contactName || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Contact Role</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.contactRole ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.contactRole || 'Missing'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Contact Phone</label>
                  <p className={cn(
                    "text-sm p-2 rounded-lg bg-dark-700/50",
                    selectedCase.contactPhone ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.contactPhone || 'Missing'}
                  </p>
                </div>

                <div className="col-span-2 space-y-1">
                  <label className="text-xs text-dark-400 uppercase tracking-wider">Transcript</label>
                  <div className={cn(
                    "text-sm p-3 rounded-lg bg-dark-700/50 max-h-48 overflow-y-auto whitespace-pre-wrap",
                    selectedCase.transcript ? "text-white" : "text-red-400 italic"
                  )}>
                    {selectedCase.transcript || 'Missing'}
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-dark-700 flex justify-end">
              <Button variant="secondary" onClick={closeModal}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserPortal;
