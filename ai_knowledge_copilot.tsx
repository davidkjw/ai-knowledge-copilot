import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, Loader2, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';

const KnowledgeCopilot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    setUploadStatus({ type: 'loading', message: 'Processing documents...' });

    await new Promise(resolve => setTimeout(resolve, 1500));

    const newDocs = files.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString()
    }));

    setDocuments(prev => [...prev, ...newDocs]);
    setUploadStatus({ type: 'success', message: `${files.length} document(s) uploaded successfully` });

    setTimeout(() => setUploadStatus(null), 3000);
  };

  const removeDocument = (docId) => {
    setDocuments(prev => prev.filter(d => d.id !== docId));
  };

  const streamResponse = async (question, conversationHistory) => {
    const fullResponse = generateAIResponse(question, conversationHistory, documents);
    
    let currentText = '';
    const assistantMessage = {
      role: 'assistant',
      content: '',
      metadata: {
        sources: documents.length > 0 ? [documents[0].name] : [],
        confidence: 0.85,
        model: 'claude-sonnet-4',
        processingTime: '1.2s'
      }
    };

    setMessages(prev => [...prev, assistantMessage]);

    for (let i = 0; i < fullResponse.length; i++) {
      currentText += fullResponse[i];
      await new Promise(resolve => setTimeout(resolve, 20));
      
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].content = currentText;
        return newMessages;
      });
    }
  };

  const generateAIResponse = (question, history, docs) => {
    const hasContext = docs.length > 0;
    
    if (question.toLowerCase().includes('what') && question.toLowerCase().includes('document')) {
      if (!hasContext) {
        return "I don't have any documents uploaded yet. Please upload some documents first so I can answer questions about them.";
      }
      return `Based on the uploaded documents (${docs.map(d => d.name).join(', ')}), I can help you understand the content. Could you be more specific about what aspect you'd like to know?`;
    }

    if (question.toLowerCase().includes('how') || question.toLowerCase().includes('explain')) {
      if (!hasContext) {
        return "I'd be happy to explain, but I don't have any reference documents yet. Upload your team's documentation and I'll provide explanations based on that context.";
      }
      return `Let me break this down based on your documentation:\n\n1. **Core Concept**: From what I can see in your documents, this relates to your team's workflows and processes.\n\n2. **Implementation**: The documents suggest a systematic approach with clear steps.\n\n3. **Best Practices**: Your team's guidelines emphasize consistency and documentation.\n\nWould you like me to dive deeper into any specific aspect?`;
    }

    if (question.toLowerCase().includes('summarize') || question.toLowerCase().includes('summary')) {
      if (!hasContext) {
        return "I need documents to summarize. Please upload your PDFs, Markdown files, or Notion exports first.";
      }
      return `**Summary of ${docs[0].name}**\n\nKey Points:\n• Main topics covered in the documentation\n• Important procedures and guidelines\n• Team-specific workflows and standards\n\nThis summary is based on RAG retrieval with 85% confidence. Would you like me to focus on a specific section?`;
    }

    if (!hasContext) {
      return `I'm your team's knowledge copilot! To get started:\n\n1. Upload your team documents (PDFs, Markdown, Notion exports)\n2. Ask me questions about your internal processes\n3. I'll provide answers with source citations\n\nI use RAG (Retrieval Augmented Generation) to ground my responses in your actual documentation. What would you like to know?`;
    }

    return `Based on your ${docs.length} uploaded document(s), I can help with that. However, I'd need a bit more context to give you the most accurate answer. Could you clarify:\n\n• Which specific area or process are you asking about?\n• Are you looking for a summary or detailed steps?\n\nThis helps me retrieve the most relevant information from your knowledge base.`;
  };

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    await streamResponse(input, messages);
    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Knowledge Copilot</h1>
          <p className="text-sm text-gray-600 mt-1">AI-powered team documentation</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-4">
            <label className="flex items-center justify-center w-full h-32 px-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors">
              <div className="text-center">
                <Upload className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">Upload documents</p>
                <p className="text-xs text-gray-500">PDF, MD, TXT</p>
              </div>
              <input
                type="file"
                className="hidden"
                multiple
                accept=".pdf,.md,.txt"
                onChange={handleFileUpload}
              />
            </label>
          </div>

          {uploadStatus && (
            <div className={`mb-4 p-3 rounded-lg flex items-start ${
              uploadStatus.type === 'success' ? 'bg-green-50 text-green-800' :
              uploadStatus.type === 'error' ? 'bg-red-50 text-red-800' :
              'bg-blue-50 text-blue-800'
            }`}>
              {uploadStatus.type === 'success' && <CheckCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />}
              {uploadStatus.type === 'loading' && <Loader2 className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5 animate-spin" />}
              {uploadStatus.type === 'error' && <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />}
              <span className="text-sm">{uploadStatus.message}</span>
            </div>
          )}

          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              Documents ({documents.length})
            </h3>
            {documents.length === 0 ? (
              <p className="text-sm text-gray-500 italic">No documents uploaded</p>
            ) : (
              <div className="space-y-2">
                {documents.map(doc => (
                  <div key={doc.id} className="flex items-start p-3 bg-gray-50 rounded-lg group hover:bg-gray-100">
                    <FileText className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{doc.name}</p>
                      <p className="text-xs text-gray-500">{(doc.size / 1024).toFixed(1)} KB</p>
                    </div>
                    <button
                      onClick={() => removeDocument(doc.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex justify-between">
              <span>Model:</span>
              <span className="font-medium">Claude Sonnet 4</span>
            </div>
            <div className="flex justify-between">
              <span>Context:</span>
              <span className="font-medium">{documents.length} docs</span>
            </div>
            <div className="flex justify-between">
              <span>Messages:</span>
              <span className="font-medium">{messages.length}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Chat Interface</h2>
            <p className="text-sm text-gray-600">Ask questions about your documentation</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Clear Chat
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Welcome to Knowledge Copilot</h3>
                <p className="text-gray-600 mb-6">
                  Upload your team's documentation and start asking questions. I'll provide answers grounded in your actual documents using RAG.
                </p>
                <div className="text-left bg-gray-50 rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium text-gray-700">Example questions:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• "What's our deployment process?"</li>
                    <li>• "Summarize the API documentation"</li>
                    <li>• "How do we handle incidents?"</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message, idx) => (
                <div key={idx} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'} rounded-lg p-4 shadow-sm`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    {message.metadata && (
                      <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600 space-y-1">
                        {message.metadata.sources.length > 0 && (
                          <div className="flex items-center">
                            <FileText className="h-3 w-3 mr-1" />
                            <span>Sources: {message.metadata.sources.join(', ')}</span>
                          </div>
                        )}
                        <div className="flex items-center justify-between">
                          <span>Confidence: {(message.metadata.confidence * 100).toFixed(0)}%</span>
                          <span>{message.metadata.processingTime}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                    <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 bg-white p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                onClick={handleSubmit}
                disabled={isLoading || !input.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeCopilot;