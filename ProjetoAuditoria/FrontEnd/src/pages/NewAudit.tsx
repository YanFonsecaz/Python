import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Globe, 
  Settings, 
  FileText, 
  Camera,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Upload,
  Search
} from 'lucide-react';
import { useAuditStore } from '../store/auditStore';
import { useNotificationStore } from '../store/notificationStore';
import { ApiService } from '../services/api';
import { Spinner } from '../components';
import type { AuditType, StartAuditRequest } from '../types';

/**
 * Página Nova Auditoria - Formulário para iniciar uma nova auditoria
 */
export function NewAudit() {
  const navigate = useNavigate();
  const { addAudit, setLoading, loading } = useAuditStore();
  const { addNotification } = useNotificationStore();
  
  // Tipo de auditoria: 'crawl' para rastreio automático, 'upload' para upload de CSV
  const [auditMode, setAuditMode] = useState<'crawl' | 'upload'>('crawl');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const [formData, setFormData] = useState<StartAuditRequest>({
    url: '',
    audit_type: 'complete',
    generate_documentation: true,
    include_screenshots: true
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});

  /**
   * Valida URL
   */
  const validateUrl = (url: string): boolean => {
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  /**
   * Valida formulário
   */
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (auditMode === 'crawl') {
      // Validação para modo de rastreio
      if (!formData.url.trim()) {
        newErrors.url = 'URL é obrigatória';
      } else if (!validateUrl(formData.url)) {
        newErrors.url = 'URL deve ser válida (incluir http:// ou https://)';
      }
    } else {
      // Validação para modo de upload
      if (!selectedFile) {
        newErrors.file = 'Arquivo CSV é obrigatório';
      } else if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        newErrors.file = 'Arquivo deve ser um CSV válido';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Manipula mudanças no formulário
   */
  const handleInputChange = (field: keyof StartAuditRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Remove erro do campo quando usuário começa a digitar
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  /**
   * Manipula seleção de arquivo
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Remove erro do arquivo quando selecionado
      if (errors.file) {
        setErrors(prev => ({
          ...prev,
          file: ''
        }));
      }
    }
  };

  /**
   * Manipula mudança de modo de auditoria
   */
  const handleModeChange = (mode: 'crawl' | 'upload') => {
    setAuditMode(mode);
    setErrors({}); // Limpa erros ao trocar de modo
    setSelectedFile(null); // Limpa arquivo selecionado
  };

  /**
   * Submete formulário
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      let response;
      
      if (auditMode === 'crawl') {
        // Modo de rastreio automático
        response = await ApiService.startAudit(formData);
      } else {
        // Modo de upload de CSV
        response = await ApiService.startAuditWithFile(selectedFile!, formData);
      }
      
      if (response.audit_id) {
        // Adiciona auditoria ao store
        const newAudit = {
          id: response.audit_id,
          url: auditMode === 'crawl' ? formData.url : `Upload: ${selectedFile?.name}`,
          status: 'pending' as const,
          progress: 0,
          created_at: new Date().toISOString(),
          audit_type: formData.audit_type,
          generate_documentation: formData.generate_documentation,
          include_screenshots: formData.include_screenshots
        };
        
        addAudit(newAudit);
        
        addNotification({
          type: 'success',
          title: 'Auditoria Iniciada',
          message: auditMode === 'crawl' 
            ? 'A auditoria foi iniciada com sucesso!' 
            : 'O arquivo CSV foi enviado e a auditoria foi iniciada!'
        });
        
        // Redireciona para página de progresso
        navigate(`/audit/progress/${response.audit_id}`);
      } else {
        throw new Error('Erro ao iniciar auditoria');
      }
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: error.message || 'Erro ao iniciar auditoria'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Opções de tipo de auditoria
   */
  const auditTypeOptions = [
    {
      value: 'complete' as AuditType,
      label: 'Auditoria Completa',
      description: 'Análise completa de SEO, performance e aspectos técnicos',
      icon: Settings,
      recommended: true
    },
    {
      value: 'basic' as AuditType,
      label: 'Auditoria Básica',
      description: 'Análise básica de SEO e estrutura da página',
      icon: CheckCircle,
      recommended: false
    },
    {
      value: 'technical' as AuditType,
      label: 'Auditoria Técnica',
      description: 'Foco em aspectos técnicos e performance',
      icon: AlertCircle,
      recommended: false
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 shadow-glow mb-6">
          <Settings className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 via-secondary-500 to-accent-500 bg-clip-text text-transparent font-poppins">
          Nova Auditoria SEO
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 font-inter max-w-2xl mx-auto">
          Configure e inicie uma nova auditoria completa para seu website com análise avançada
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Seleção de Modo de Auditoria */}
        <div className="glass-card hover:shadow-glow transition-all duration-300">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
              <Settings className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">
                Modo de Auditoria
              </h2>
              <p className="text-gray-600 dark:text-gray-300 font-inter">
                Escolha como deseja realizar a auditoria do seu website
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Rastreio Automático */}
            <div 
              className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-300 ${
                auditMode === 'crawl' 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-lg' 
                  : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600'
              }`}
              onClick={() => handleModeChange('crawl')}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${
                  auditMode === 'crawl' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                }`}>
                  <Search className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Rastreio Automático
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                O sistema irá rastrear automaticamente seu website usando o Screaming Frog para coletar todos os dados necessários
              </p>
            </div>

            {/* Upload de CSV */}
            <div 
              className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-300 ${
                auditMode === 'upload' 
                  ? 'border-secondary-500 bg-secondary-50 dark:bg-secondary-900/20 shadow-lg' 
                  : 'border-gray-200 dark:border-gray-700 hover:border-secondary-300 dark:hover:border-secondary-600'
              }`}
              onClick={() => handleModeChange('upload')}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${
                  auditMode === 'upload' 
                    ? 'bg-secondary-500 text-white' 
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                }`}>
                  <Upload className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Upload de CSV
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Faça upload de um arquivo CSV exportado diretamente do Screaming Frog para análise
              </p>
            </div>
          </div>
        </div>

        {/* Conteúdo Condicional baseado no modo */}
        {auditMode === 'crawl' ? (
          /* URL Input */
          <div className="glass-card hover:shadow-glow transition-all duration-300 group">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg group-hover:shadow-blue-500/25 transition-all duration-300">
                <Globe className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">
                  URL do Website
                </h2>
                <p className="text-gray-600 dark:text-gray-300 font-inter">
                  Digite a URL completa do website que deseja auditar
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="label text-lg font-semibold">
                  URL *
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => handleInputChange('url', e.target.value)}
                    placeholder="https://exemplo.com"
                    className={`input text-lg ${errors.url ? 'border-red-500 focus:border-red-500' : ''}`}
                  />
                  <Globe className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400" />
                </div>
                {errors.url && (
                  <p className="text-red-500 text-sm mt-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {errors.url}
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* File Upload */
          <div className="glass-card hover:shadow-glow transition-all duration-300 group">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg group-hover:shadow-green-500/25 transition-all duration-300">
                <Upload className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">
                  Upload do Arquivo CSV
                </h2>
                <p className="text-gray-600 dark:text-gray-300 font-inter">
                  Faça upload do arquivo CSV exportado do Screaming Frog
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="label text-lg font-semibold">
                  Arquivo CSV do Screaming Frog *
                </label>
                <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                  selectedFile 
                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                    : errors.file 
                      ? 'border-red-500 bg-red-50 dark:bg-red-900/20' 
                      : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
                }`}>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="csv-upload"
                  />
                  <label htmlFor="csv-upload" className="cursor-pointer">
                    <div className="space-y-4">
                      <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center ${
                        selectedFile 
                          ? 'bg-green-500' 
                          : errors.file 
                            ? 'bg-red-500' 
                            : 'bg-gray-400'
                      }`}>
                        <Upload className="w-8 h-8 text-white" />
                      </div>
                      {selectedFile ? (
                        <div>
                          <p className="text-lg font-semibold text-green-700 dark:text-green-400">
                            Arquivo selecionado: {selectedFile.name}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Tamanho: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      ) : (
                        <div>
                          <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                            Clique para selecionar ou arraste o arquivo aqui
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Apenas arquivos CSV são aceitos
                          </p>
                        </div>
                      )}
                    </div>
                  </label>
                </div>
                {errors.file && (
                  <p className="text-red-500 text-sm mt-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {errors.file}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tipo de Auditoria */}
        <div className="glass-card hover:shadow-glow transition-all duration-300 group">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg group-hover:shadow-green-500/25 transition-all duration-300">
              <Settings className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">
                Tipo de Auditoria
              </h2>
              <p className="text-gray-600 dark:text-gray-300 font-inter">
                Selecione o nível de análise desejado para sua auditoria
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {auditTypeOptions.map((option) => {
              const IconComponent = option.icon;
              const isSelected = formData.audit_type === option.value;
              
              return (
                <div
                  key={option.value}
                  className={`relative p-6 rounded-xl border-2 cursor-pointer transition-all duration-300 group/card ${
                    isSelected
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-lg shadow-primary-500/25'
                      : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:shadow-lg'
                  }`}
                  onClick={() => handleInputChange('audit_type', option.value)}
                >
                  {option.recommended && (
                    <div className="absolute -top-2 -right-2 bg-gradient-to-r from-accent-500 to-accent-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                      Recomendado
                    </div>
                  )}
                  
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-3 rounded-lg transition-all duration-300 ${
                      isSelected
                        ? 'bg-primary-500 text-white shadow-lg'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 group-hover/card:bg-primary-100 dark:group-hover/card:bg-primary-900/30'
                    }`}>
                      <IconComponent className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                        {option.label}
                      </h3>
                    </div>
                    <div className={`w-5 h-5 rounded-full border-2 transition-all duration-300 ${
                      isSelected
                        ? 'border-primary-500 bg-primary-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}>
                      {isSelected && (
                        <CheckCircle className="w-full h-full text-white" />
                      )}
                    </div>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                    {option.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Opções Adicionais */}
        <div className="glass-card hover:shadow-glow transition-all duration-300 group">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl shadow-lg group-hover:shadow-orange-500/25 transition-all duration-300">
              <Settings className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">
                Opções Adicionais
              </h2>
              <p className="text-gray-600 dark:text-gray-300 font-inter">
                Configure recursos extras para sua auditoria
              </p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Gerar Documentação */}
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Gerar Documentação
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Cria um relatório detalhado em PDF com todas as descobertas
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.generate_documentation}
                  onChange={(e) => handleInputChange('generate_documentation', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {/* Incluir Screenshots */}
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <Camera className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Incluir Screenshots
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Captura screenshots das páginas durante a auditoria
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.include_screenshots}
                  onChange={(e) => handleInputChange('include_screenshots', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Botão de Submit */}
        <div className="flex justify-center pt-8">
          <button
            type="submit"
            disabled={loading}
            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl hover:shadow-primary-500/25 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? (
              <>
                <Spinner className="w-6 h-6" />
                Iniciando Auditoria...
              </>
            ) : (
              <>
                <Settings className="w-6 h-6 group-hover:rotate-90 transition-transform duration-300" />
                Iniciar Auditoria
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}