import React, { useState } from 'react';
import { UploadCloud, File, Image as ImageIcon, X } from 'lucide-react';
import { motion } from 'framer-motion';

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
            className={`relative w-full rounded-2xl border-2 border-dashed p-10 transition-all duration-300 text-center cursor-pointer overflow-hidden
        ${dragActive ? 'border-brand-500 bg-brand-500/10 shadow-[0_0_20px_rgba(69,243,255,0.2)]' : 'border-white/20 glass-panel hover:border-brand-500/50 hover:bg-white/5'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload').click()}
        >
            {dragActive && <div className="absolute inset-0 bg-brand-500/5 blur-xl pointer-events-none"></div>}
            
            <input
                id="file-upload"
                type="file"
                multiple={false}
                onChange={handleChange}
                className="hidden"
                accept="image/*,.pdf,.txt,.doc,.docx"
            />

            {!selectedFile ? (
                <div className="flex flex-col items-center justify-center space-y-5 relative z-10">
                    <motion.div 
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="p-5 bg-gradient-to-br from-brand-600 to-brand-400 rounded-2xl text-deepSpace shadow-neon"
                    >
                        <UploadCloud size={40} />
                    </motion.div>
                    <div>
                        <p className="text-xl font-bold text-white tracking-wide">Click to upload or drag and drop</p>
                        <p className="text-sm text-slate-400 mt-2 font-medium">Images (X-Ray, MRI) or Text Clinical Notes <br/> <span className="text-xs text-brand-500 opacity-80">(Max 50MB)</span></p>
                    </div>
                </div>
            ) : (
                <div className="flex items-center justify-between p-5 bg-white/5 border border-white/10 rounded-xl hover:border-brand-500/30 transition-colors relative z-10 backdrop-blur-md shadow-lg">
                    <div className="flex items-center space-x-4">
                        <div className="p-3 bg-brand-500/20 rounded-lg border border-brand-500/30">
                            {selectedFile.type.includes('image') ? (
                                <ImageIcon className="text-brand-400 w-8 h-8" />
                            ) : (
                                <File className="text-brand-400 w-8 h-8" />
                            )}
                        </div>
                        <div className="text-left">
                            <p className="font-bold text-white text-base truncate max-w-[200px] sm:max-w-xs">
                                {selectedFile.name}
                            </p>
                            <p className="text-xs text-slate-400 font-medium">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.type || "Unknown File Type"}
                            </p>
                        </div>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.1, rotate: 90 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={clearFile}
                        className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/20 rounded-lg transition-colors border border-transparent hover:border-red-500/30"
                    >
                        <X size={20} />
                    </motion.button>
                </div>
            )}
        </div>
    );
};

export default UploadBox;
