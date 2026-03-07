import React, { useState } from 'react';
import { UploadCloud, File, Image as ImageIcon, X } from 'lucide-react';

const UploadBox = ({ onFileSelect }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
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
        if (onFileSelect) onFileSelect(file);
    };

    const clearFile = (e) => {
        e.stopPropagation();
        setSelectedFile(null);
        if (onFileSelect) onFileSelect(null);
    };

    return (
        <div
            className={`relative w-full rounded-2xl border-2 border-dashed p-8 transition-colors text-center cursor-pointer 
        ${dragActive ? 'border-brand-500 bg-brand-50' : 'border-slate-300 bg-white hover:bg-slate-50'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload').click()}
        >
            <input
                id="file-upload"
                type="file"
                multiple={false}
                onChange={handleChange}
                className="hidden"
                accept="image/*,.pdf,.txt,.doc,.docx"
            />

            {!selectedFile ? (
                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="p-4 bg-brand-50 rounded-full text-brand-600">
                        <UploadCloud size={32} />
                    </div>
                    <div>
                        <p className="text-lg font-medium text-slate-700">Click to upload or drag and drop</p>
                        <p className="text-sm text-slate-500 mt-1">Images (X-Ray, MRI) or Text Clinical Notes</p>
                    </div>
                </div>
            ) : (
                <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                        {selectedFile.type.includes('image') ? (
                            <ImageIcon className="text-brand-500 w-8 h-8" />
                        ) : (
                            <File className="text-brand-500 w-8 h-8" />
                        )}
                        <div className="text-left">
                            <p className="font-medium text-slate-800 text-sm truncate max-w-[200px]">
                                {selectedFile.name}
                            </p>
                            <p className="text-xs text-slate-500">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={clearFile}
                        className="p-1.5 text-slate-400 hover:text-danger hover:bg-danger/10 rounded-md transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>
            )}
        </div>
    );
};

export default UploadBox;
