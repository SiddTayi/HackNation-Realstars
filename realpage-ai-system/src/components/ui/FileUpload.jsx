import { useState, useRef } from 'react';
import { Upload, FileSpreadsheet, X, CheckCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

export function FileUpload({ onFileSelect, accept = '.xlsx,.xls,.csv', className }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    setSelectedFile(file);
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
    if (onFileSelect) {
      onFileSelect(null);
    }
  };

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'relative rounded-xl border-2 border-dashed transition-all duration-300',
          'bg-dark-800/30 hover:bg-dark-800/50',
          dragActive
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-dark-600 hover:border-primary-500/50',
          selectedFile && 'border-accent-500 bg-accent-500/5'
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />

        <div className="p-8 text-center">
          {selectedFile ? (
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-xl bg-accent-500/20 flex items-center justify-center">
                  <FileSpreadsheet className="w-8 h-8 text-accent-400" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-accent-500 flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
              </div>
              <div>
                <p className="text-white font-medium">{selectedFile.name}</p>
                <p className="text-dark-400 text-sm">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.preventDefault();
                  removeFile();
                }}
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
              >
                <X className="w-4 h-4 mr-1" />
                Remove file
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-xl bg-primary-500/20 flex items-center justify-center animate-pulse-slow">
                <Upload className="w-8 h-8 text-primary-400" />
              </div>
              <div>
                <p className="text-white font-medium mb-1">
                  Drop your Excel file here, or{' '}
                  <span className="text-primary-400">browse</span>
                </p>
                <p className="text-dark-400 text-sm">
                  Supports: .xlsx, .xls, .csv (Max 10MB)
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
