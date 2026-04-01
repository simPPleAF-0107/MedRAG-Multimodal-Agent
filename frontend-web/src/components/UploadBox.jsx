import React, { useState } from 'react';
import { UploadCloud, File, Image as ImageIcon, X } from 'lucide-react';
import { motion } from 'framer-motion';

const UploadBox = ({ onFilesSelect }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState([]);

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

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files.length > 0) {
            handleFiles(Array.from(e.target.files));
        }
    };

    const handleFiles = (newFiles) => {
        const updatedFiles = [...selectedFiles, ...newFiles];
        setSelectedFiles(updatedFiles);
        if (onFilesSelect) onFilesSelect(updatedFiles);
    };

    const removeFile = (e, indexToRemove) => {
        e.stopPropagation();
        const updatedFiles = selectedFiles.filter((_, index) => index !== indexToRemove);
        setSelectedFiles(updatedFiles);
        if (onFilesSelect) onFilesSelect(updatedFiles);
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
                multiple={true}
                onChange={handleChange}
                className="hidden"
                accept="image/*,.pdf,.txt,.doc,.docx"
            />

            {selectedFiles.length === 0 ? (
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
                        <p className="text-sm text-slate-400 mt-2 font-medium">Images (X-Ray, MRI) or Text Clinical Notes <br/> <span className="text-xs text-brand-500 opacity-80">(Multiple allowed)</span></p>
                    </div>
                </div>
            ) : (
                <div className="space-y-3 relative z-10 w-full" onClick={(e) => e.stopPropagation()}>
                    <div className="flex justify-between items-center mb-4">
                        <span className="text-slate-300 font-medium">{selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} attached</span>
                        <button 
                            type="button"
                            onClick={() => document.getElementById('file-upload').click()}
                            className="px-3 py-1 bg-white/10 hover:bg-brand-500/20 text-brand-400 text-sm rounded-lg transition-colors"
                        >
                            + Add More
                        </button>
                    </div>
                    {selectedFiles.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:border-brand-500/30 transition-colors backdrop-blur-md shadow-lg">
                            <div className="flex items-center space-x-4">
                                <div className="p-2 bg-brand-500/20 rounded-lg border border-brand-500/30">
                                    {file.type.includes('image') ? (
                                        <ImageIcon className="text-brand-400 w-6 h-6" />
                                    ) : (
                                        <File className="text-brand-400 w-6 h-6" />
                                    )}
                                </div>
                                <div className="text-left w-full">
                                    <p className="font-bold text-white text-sm truncate max-w-[150px] sm:max-w-xs">
                                        {file.name}
                                    </p>
                                    <p className="text-xs text-slate-400 font-medium">
                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                            <motion.button
                                type="button"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={(e) => removeFile(e, idx)}
                                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                            >
                                <X size={18} />
                            </motion.button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default UploadBox;
