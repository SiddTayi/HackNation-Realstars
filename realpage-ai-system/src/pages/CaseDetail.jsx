import { useState } from 'react';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Edit3,
  Save,
  Clock,
  User,
  Tag,
  AlertTriangle,
  FileText,
  Sparkles,
  Database,
  Brain,
} from 'lucide-react';
import { Header } from '../components/layout/Header';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardFooter } from '../components/ui/Card';
import { Badge, PriorityBadge, StatusBadge } from '../components/ui/Badge';
import { Textarea } from '../components/ui/Input';
import { Chatbot } from '../components/Chatbot';
import { caseAPI, knowledgeAPI } from '../services/api';
import { cn, formatDate } from '../lib/utils';

export function CaseDetail({ caseData, user, onLogout, onBack }) {
  const [resolution, setResolution] = useState(caseData.aiResolution || '');
  const [isEditing, setIsEditing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionTaken, setActionTaken] = useState(null);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await caseAPI.updateCaseStatus(caseData.caseId, 'approved', resolution);
      await knowledgeAPI.addToKnowledgeBase({
        caseId: caseData.caseId,
        issue: caseData.issue,
        resolution: resolution,
        category: caseData.category,
      });
      setActionTaken('approved');
    } catch (error) {
      console.error('Error approving case:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      await caseAPI.updateCaseStatus(caseData.caseId, 'rejected', resolution);
      setActionTaken('rejected');
    } catch (error) {
      console.error('Error rejecting case:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveEdit = async () => {
    setIsSubmitting(true);
    try {
      await caseAPI.updateCaseStatus(caseData.caseId, 'edited', resolution);
      await knowledgeAPI.addToKnowledgeBase({
        caseId: caseData.caseId,
        issue: caseData.issue,
        resolution: resolution,
        category: caseData.category,
      });
      setIsEditing(false);
      setActionTaken('edited');
    } catch (error) {
      console.error('Error saving edit:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (actionTaken) {
    return (
      <div className="min-h-screen bg-mesh flex flex-col">
        <Header user={user} onLogout={onLogout} />
        <main className="flex-1 pt-24 pb-12 flex items-center justify-center">
          <Card className="max-w-md w-full mx-4">
            <CardContent className="p-8 text-center">
              <div
                className={cn(
                  'w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6',
                  actionTaken === 'approved' && 'bg-accent-500/20',
                  actionTaken === 'rejected' && 'bg-red-500/20',
                  actionTaken === 'edited' && 'bg-primary-500/20'
                )}
              >
                {actionTaken === 'approved' && (
                  <CheckCircle className="w-10 h-10 text-accent-400" />
                )}
                {actionTaken === 'rejected' && (
                  <XCircle className="w-10 h-10 text-red-400" />
                )}
                {actionTaken === 'edited' && (
                  <Edit3 className="w-10 h-10 text-primary-400" />
                )}
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                {actionTaken === 'approved' && 'Case Approved!'}
                {actionTaken === 'rejected' && 'Case Rejected'}
                {actionTaken === 'edited' && 'Resolution Updated!'}
              </h2>
              <p className="text-dark-400 mb-6">
                {actionTaken === 'approved' &&
                  'The resolution has been added to the knowledge base for future reference.'}
                {actionTaken === 'rejected' &&
                  'The case has been marked as rejected. Consider providing a better solution.'}
                {actionTaken === 'edited' &&
                  'Your updated resolution has been saved and added to the knowledge base.'}
              </p>
              <div className="flex items-center justify-center gap-2 mb-6">
                <Badge variant="primary">{caseData.caseId}</Badge>
                <StatusBadge status={actionTaken} />
              </div>
              <Button onClick={onBack} className="w-full">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mesh flex flex-col">
      <Header user={user} onLogout={onLogout} />

      <main className="flex-1 pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back Button & Header */}
          <div className="mb-6">
            <Button variant="ghost" onClick={onBack} className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Cases
            </Button>
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-bold text-white">{caseData.caseId}</h1>
                  <PriorityBadge priority={caseData.priority} />
                  <StatusBadge status={caseData.status} />
                </div>
                <p className="text-dark-400">
                  Submitted by {caseData.submittedBy} • {formatDate(caseData.createdAt)}
                </p>
              </div>
            </div>
          </div>

          {/* Two-Panel Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Panel - Case Details (1/3) */}
            <div className="lg:col-span-4">
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary-400" />
                    <h2 className="text-lg font-semibold text-white">Case Details</h2>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Case ID */}
                  <div className="bg-gradient-to-r from-primary-500/20 to-cyan-500/20 rounded-lg p-3 border border-primary-500/30">
                    <div className="flex items-center gap-2 text-dark-400 text-xs mb-1">
                      <Tag className="w-3 h-3" />
                      Case ID
                    </div>
                    <p className="text-primary-400 font-mono font-bold">{caseData.caseId}</p>
                  </div>

                  {/* Excel Data Fields */}
                  <div className="space-y-3">
                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Conversation ID</div>
                      <p className="text-white font-medium text-sm">{caseData.conversationId || 'N/A'}</p>
                    </div>
                    
                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Channel</div>
                      <p className="text-white font-medium text-sm">{caseData.channel || 'N/A'}</p>
                    </div>

                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Created Date</div>
                      <p className="text-white font-medium text-sm">{caseData.createdDate || formatDate(caseData.createdAt)}</p>
                    </div>

                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Customer Role</div>
                      <p className="text-white font-medium text-sm">{caseData.customerRole || 'N/A'}</p>
                    </div>

                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="flex items-center gap-2 text-dark-400 text-xs mb-1">
                        <User className="w-3 h-3" />
                        First Tier Agent
                      </div>
                      <p className="text-white font-medium text-sm">{caseData.agentName || caseData.submittedBy || 'Unassigned'}</p>
                    </div>

                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Product</div>
                      <p className="text-white font-medium text-sm">{caseData.product || 'N/A'}</p>
                    </div>

                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Account Name</div>
                      <p className="text-white font-medium text-sm">{caseData.accountName || 'N/A'}</p>
                    </div>

                    {/* Property Info */}
                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Property</div>
                      <p className="text-white font-medium text-sm">
                        {caseData.propertyName || 'N/A'}
                        {caseData.propertyCity && `, ${caseData.propertyCity}`}
                        {caseData.propertyState && `, ${caseData.propertyState}`}
                      </p>
                    </div>

                    {/* Contact Info */}
                    <div className="bg-dark-700/30 rounded-lg p-3">
                      <div className="text-dark-400 text-xs mb-1">Contact</div>
                      <p className="text-white font-medium text-sm">
                        {caseData.contactName || 'N/A'}
                        {caseData.contactRole && ` (${caseData.contactRole})`}
                      </p>
                      {caseData.contactPhone && (
                        <p className="text-dark-400 text-xs mt-1">{caseData.contactPhone}</p>
                      )}
                    </div>
                  </div>

                  {/* Transcript */}
                  {caseData.transcript && (
                    <div>
                      <label className="text-sm font-medium text-dark-400 mb-2 block">
                        Transcript
                      </label>
                      <div className="bg-dark-700/50 rounded-lg p-3 border border-dark-600 max-h-40 overflow-y-auto scrollbar-thin">
                        <p className="text-dark-200 text-sm whitespace-pre-wrap">{caseData.transcript}</p>
                      </div>
                    </div>
                  )}

                  {/* Info Box */}
                  <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Brain className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-white text-sm font-medium mb-1">AI Analysis</p>
                        <p className="text-dark-300 text-xs">
                          Resolution generated using RAG search with 85% confidence.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Panel - AI Recommended Resolution (2/3) */}
            <div className="lg:col-span-8">
              <Card className="h-full flex flex-col">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-accent-400" />
                      <h2 className="text-lg font-semibold text-white">AI Recommended Resolution</h2>
                    </div>
                    {!isEditing && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsEditing(true)}
                      >
                        <Edit3 className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="flex-1">
                  {isEditing ? (
                    <Textarea
                      value={resolution}
                      onChange={(e) => setResolution(e.target.value)}
                      className="h-full min-h-[400px] resize-none"
                      placeholder="Enter the resolution..."
                    />
                  ) : (
                    <div className="bg-dark-700/50 rounded-lg p-6 border border-dark-600 h-full min-h-[400px] overflow-y-auto scrollbar-thin">
                      <p className="text-dark-200 whitespace-pre-wrap leading-relaxed">
                        {resolution}
                      </p>
                    </div>
                  )}
                </CardContent>
                <CardFooter>
                  <div className="w-full space-y-4">
                    {isEditing ? (
                      <div className="flex gap-3">
                        <Button
                          variant="secondary"
                          className="flex-1"
                          onClick={() => {
                            setIsEditing(false);
                            setResolution(caseData.aiResolution);
                          }}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="success"
                          className="flex-1"
                          onClick={handleSaveEdit}
                          loading={isSubmitting}
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Save & Submit
                        </Button>
                      </div>
                    ) : (
                      <>
                        <div className="flex gap-3">
                          <Button
                            variant="success"
                            className="flex-1"
                            onClick={handleApprove}
                            loading={isSubmitting}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approve
                          </Button>
                          <Button
                            variant="danger"
                            className="flex-1"
                            onClick={handleReject}
                            loading={isSubmitting}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </Button>
                        </div>
                        <p className="text-dark-500 text-xs text-center">
                          Approved resolutions are automatically added to the knowledge base
                        </p>
                      </>
                    )}
                  </div>
                </CardFooter>
              </Card>
            </div>
          </div>

          {/* Floating Chatbot */}
          <Chatbot caseContext={caseData} isFloating={true} />

          {/* Knowledge Base Info */}
          <div className="mt-6">
            <Card className="bg-gradient-to-r from-primary-900/30 via-cyan-900/30 to-accent-900/30 border-primary-500/20">
              <CardContent className="p-6">
                <div className="flex items-center gap-6 flex-wrap">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                      <Database className="w-6 h-6 text-primary-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">Self-Learning System</h3>
                      <p className="text-dark-400 text-sm">
                        Every approved resolution improves our AI
                      </p>
                    </div>
                  </div>
                  <div className="flex-1 grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-white">12,453</p>
                      <p className="text-dark-400 text-xs">Knowledge Entries</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">98.2%</p>
                      <p className="text-dark-400 text-xs">Accuracy Rate</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">2.3s</p>
                      <p className="text-dark-400 text-xs">Avg. Resolution Time</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

export default CaseDetail;
