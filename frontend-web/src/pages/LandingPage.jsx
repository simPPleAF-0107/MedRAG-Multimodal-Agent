import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import {
    Activity, Brain, Shield, Zap, Users, FileText, Stethoscope,
    ChevronRight, ArrowRight, Mic, Image, FileSearch, CheckCircle2,
    Lock, Eye, Smartphone, Globe, Cloud, Star, Sparkles, Heart,
    BarChart3, AlertTriangle, GraduationCap, BadgeCheck
} from 'lucide-react';

// ── Animation variants ──────────────────────────────────────────────────────
const fadeUp = {
    hidden: { opacity: 0, y: 40 },
    visible: (i = 0) => ({
        opacity: 1, y: 0,
        transition: { delay: i * 0.1, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }
    })
};

const stagger = {
    visible: { transition: { staggerChildren: 0.08 } }
};

// ── Reusable Section Wrapper ────────────────────────────────────────────────
const Section = ({ children, className = '', id }) => (
    <section id={id} className={`relative py-24 md:py-32 px-6 md:px-12 lg:px-20 ${className}`}>
        {children}
    </section>
);

// ── Glassmorphic Card ───────────────────────────────────────────────────────
const GlassCard = ({ children, className = '', hover = true }) => (
    <motion.div
        variants={fadeUp}
        whileHover={hover ? { y: -6, scale: 1.02 } : {}}
        className={`relative bg-white/[0.03] backdrop-blur-xl border border-white/[0.06] rounded-3xl overflow-hidden transition-all duration-500 ${hover ? 'hover:border-cyan-400/30 hover:shadow-[0_8px_40px_rgba(0,212,255,0.08)]' : ''} ${className}`}
    >
        {children}
    </motion.div>
);

// ═══════════════════════════════════════════════════════════════════════════
//  LANDING PAGE
// ═══════════════════════════════════════════════════════════════════════════

const LandingPage = () => {
    const navigate = useNavigate();
    const { scrollYProgress } = useScroll();
    const headerOpacity = useTransform(scrollYProgress, [0, 0.05], [0, 1]);

    return (
        <div className="min-h-screen bg-[#04060C] text-white overflow-x-hidden">

            {/* ── FLOATING NAVBAR ──────────────────────────────────────── */}
            <motion.nav
                style={{ opacity: headerOpacity }}
                className="fixed top-0 left-0 right-0 z-50 backdrop-blur-2xl bg-[#04060C]/70 border-b border-white/5"
            >
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
                            <Activity className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-lg font-black tracking-wider">MedRAG</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
                        <a href="#features" className="hover:text-white transition-colors">Features</a>
                        <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
                        <a href="#use-cases" className="hover:text-white transition-colors">Use Cases</a>
                        <a href="#security" className="hover:text-white transition-colors">Security</a>
                    </div>
                    <div className="flex items-center gap-3">
                        <button onClick={() => navigate('/login')}
                            className="px-5 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">
                            Sign In
                        </button>
                        <button onClick={() => navigate('/register')}
                            className="px-5 py-2.5 text-sm font-bold bg-gradient-to-r from-cyan-500 to-blue-600 rounded-xl hover:shadow-[0_4px_20px_rgba(0,212,255,0.3)] transition-all">
                            Get Started
                        </button>
                    </div>
                </div>
            </motion.nav>

            {/* ── HERO SECTION ─────────────────────────────────────────── */}
            <Section className="min-h-screen flex items-center justify-center text-center relative">
                {/* Ambient background */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-cyan-500/8 rounded-full blur-[150px] animate-pulse" />
                    <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-blue-600/6 rounded-full blur-[180px] animate-pulse" style={{ animationDelay: '2s' }} />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-500/4 rounded-full blur-[200px]" />
                    {/* Grid lines */}
                    <div className="absolute inset-0" style={{
                        backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
                        backgroundSize: '60px 60px'
                    }} />
                </div>

                <motion.div initial="hidden" animate="visible" variants={stagger}
                    className="relative z-10 max-w-5xl mx-auto">

                    <motion.div variants={fadeUp} custom={0}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-cyan-400 mb-8 tracking-widest uppercase">
                        <Sparkles className="w-3.5 h-3.5" />
                        Built for clinicians. Accessible for everyone.
                    </motion.div>

                    <motion.h1 variants={fadeUp} custom={1}
                        className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter leading-[0.9] mb-8">
                        Your AI Medical{' '}
                        <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                            Intelligence
                        </span>{' '}
                        System.
                    </motion.h1>

                    <motion.p variants={fadeUp} custom={2}
                        className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-4 leading-relaxed font-medium">
                        MedRAG combines advanced retrieval, multimodal AI, and clinical reasoning to deliver
                        faster, safer, and more accurate medical insights — from symptoms to diagnosis.
                    </motion.p>

                    <motion.p variants={fadeUp} custom={3}
                        className="text-base text-cyan-400/60 font-semibold mb-10">
                        Instant. Reliable. Multimodal.
                    </motion.p>

                    <motion.div variants={fadeUp} custom={4} className="flex flex-wrap justify-center gap-4">
                        <button onClick={() => navigate('/register')}
                            className="group px-8 py-4 text-base font-bold bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl hover:shadow-[0_8px_40px_rgba(0,212,255,0.25)] transition-all flex items-center gap-2">
                            Get Started <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button onClick={() => {
                            document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                        }}
                            className="px-8 py-4 text-base font-bold border border-white/10 rounded-2xl text-gray-300 hover:bg-white/5 hover:border-white/20 transition-all">
                            View Demo
                        </button>
                    </motion.div>

                    {/* Trust bar */}
                    <motion.div variants={fadeUp} custom={5}
                        className="mt-16 flex flex-wrap justify-center gap-8 text-xs text-gray-500 font-medium uppercase tracking-widest">
                        <span className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyan-500/50" /> HIPAA Aligned</span>
                        <span className="flex items-center gap-2"><Lock className="w-4 h-4 text-cyan-500/50" /> End-to-End Encrypted</span>
                        <span className="flex items-center gap-2"><Zap className="w-4 h-4 text-cyan-500/50" /> Real-Time Processing</span>
                        <span className="flex items-center gap-2"><Brain className="w-4 h-4 text-cyan-500/50" /> 34K+ Knowledge Nodes</span>
                    </motion.div>
                </motion.div>
            </Section>

            {/* ── WHAT IT DOES ─────────────────────────────────────────── */}
            <Section id="features">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-6xl mx-auto">

                    <motion.div variants={fadeUp} className="text-center mb-20">
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Core Value Proposition</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-6">
                            From Symptoms to Structured<br />
                            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                                Medical Insight
                            </span> — in Seconds
                        </h2>
                        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                            MedRAG is not another AI chatbot. It's a multimodal medical reasoning system that understands
                            your input and transforms it into evidence-backed clinical insight.
                        </p>
                    </motion.div>

                    {/* Input types */}
                    <div className="grid md:grid-cols-3 gap-6 mb-16">
                        {[
                            { icon: FileSearch, title: 'Text Analysis', desc: 'Symptoms, history, clinical notes — parsed and cross-referenced against 34K+ medical knowledge nodes.', accent: 'cyan' },
                            { icon: Image, title: 'Medical Imaging', desc: 'X-rays, CT scans, dermatological photos — processed through multimodal CLIP embeddings for visual reasoning.', accent: 'blue' },
                            { icon: Mic, title: 'Voice Input', desc: 'Patient descriptions captured via audio, transcribed and integrated into the diagnostic pipeline.', accent: 'indigo' },
                        ].map((item, i) => (
                            <GlassCard key={i} className="p-8">
                                <div className={`w-14 h-14 rounded-2xl bg-${item.accent}-500/10 border border-${item.accent}-500/20 flex items-center justify-center mb-6`}>
                                    <item.icon className={`w-7 h-7 text-${item.accent}-400`} />
                                </div>
                                <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                                <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
                            </GlassCard>
                        ))}
                    </div>

                    {/* Output types */}
                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[
                            { icon: CheckCircle2, text: 'Evidence-backed insights' },
                            { icon: BarChart3, text: 'Differential diagnoses' },
                            { icon: AlertTriangle, text: 'Risk-aware recommendations' },
                            { icon: BadgeCheck, text: 'Confidence scoring' },
                        ].map((item, i) => (
                            <motion.div key={i} variants={fadeUp} custom={i}
                                className="flex items-center gap-3 p-4 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
                                <item.icon className="w-5 h-5 text-cyan-400 shrink-0" />
                                <span className="text-sm font-medium text-gray-300">{item.text}</span>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── HOW IT WORKS ─────────────────────────────────────────── */}
            <Section id="how-it-works" className="bg-white/[0.01]">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-5xl mx-auto">

                    <motion.div variants={fadeUp} className="text-center mb-20">
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Pipeline</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight">
                            How It <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Works</span>
                        </h2>
                    </motion.div>

                    <div className="grid md:grid-cols-4 gap-8">
                        {[
                            { step: '01', title: 'Input', desc: 'Upload symptoms, voice notes, or medical images.', icon: FileText, color: 'cyan' },
                            { step: '02', title: 'AI Processing', desc: 'Hybrid RAG pipeline with vector + graph reasoning.', icon: Brain, color: 'blue' },
                            { step: '03', title: 'Safety Checks', desc: 'Hallucination detection + confidence scoring.', icon: Shield, color: 'indigo' },
                            { step: '04', title: 'Output', desc: 'Structured, explainable medical response.', icon: FileSearch, color: 'emerald' },
                        ].map((item, i) => (
                            <motion.div key={i} variants={fadeUp} custom={i} className="text-center relative">
                                {i < 3 && (
                                    <div className="hidden md:block absolute top-10 left-[60%] w-[80%] h-px bg-gradient-to-r from-white/10 to-transparent" />
                                )}
                                <div className={`w-20 h-20 mx-auto mb-6 rounded-3xl bg-${item.color}-500/10 border border-${item.color}-500/20 flex items-center justify-center`}>
                                    <item.icon className={`w-9 h-9 text-${item.color}-400`} />
                                </div>
                                <span className="text-cyan-500/40 text-xs font-black tracking-widest">{item.step}</span>
                                <h3 className="text-lg font-bold mt-2 mb-2">{item.title}</h3>
                                <p className="text-gray-500 text-sm">{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── WHY MEDRAG ──────────────────────────────────────────── */}
            <Section id="why-medrag">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-6xl mx-auto">

                    <motion.div variants={fadeUp} className="text-center mb-20">
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Differentiation</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight">
                            Designed for <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Trust</span>, Not Just Answers
                        </h2>
                    </motion.div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            { icon: FileSearch, title: 'Evidence-Based Outputs', desc: 'Grounded in 34,000+ medical knowledge nodes across published datasets.' },
                            { icon: Eye, title: 'Hallucination Detection', desc: 'Verifies every claim before showing results. Built-in anti-hallucination guardrails.' },
                            { icon: Zap, title: 'Real-Time Processing', desc: 'Async pipelines for near-instant response even on complex multimodal queries.' },
                            { icon: Brain, title: 'Multimodal Intelligence', desc: 'Text + Image + Audio combined reasoning through hybrid RAG architecture.' },
                            { icon: BarChart3, title: 'Confidence Scoring', desc: 'Transparent trust percentage on every diagnosis. Know how confident the AI is.' },
                            { icon: Heart, title: 'Patient-Centric Design', desc: 'Built with empathy. Accessible language, clear recommendations, actionable next steps.' },
                        ].map((item, i) => (
                            <GlassCard key={i} className="p-8">
                                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-5">
                                    <item.icon className="w-6 h-6 text-cyan-400" />
                                </div>
                                <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                                <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
                            </GlassCard>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── USE CASES ───────────────────────────────────────────── */}
            <Section id="use-cases" className="bg-white/[0.01]">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-5xl mx-auto">

                    <motion.div variants={fadeUp} className="text-center mb-20">
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Who It's For</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight">
                            One Platform.<br />
                            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Every Stakeholder.</span>
                        </h2>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { icon: Stethoscope, title: 'For Doctors', desc: 'Augment clinical decision-making with AI-backed differential diagnoses and evidence retrieval. Cut time-to-insight by 60%.', gradient: 'from-cyan-500 to-blue-600' },
                            { icon: Users, title: 'For Patients', desc: 'Understand symptoms before visiting a hospital. Get structured, plain-language explanations of complex medical topics.', gradient: 'from-blue-500 to-indigo-600' },
                            { icon: GraduationCap, title: 'For Students', desc: 'Learn diagnostics with structured reasoning outputs. Study real clinical patterns through the AI\'s transparent methodology.', gradient: 'from-indigo-500 to-purple-600' },
                        ].map((item, i) => (
                            <GlassCard key={i} className="p-10 text-center">
                                <div className={`w-20 h-20 mx-auto mb-8 rounded-3xl bg-gradient-to-br ${item.gradient} flex items-center justify-center shadow-lg`}>
                                    <item.icon className="w-10 h-10 text-white" />
                                </div>
                                <h3 className="text-2xl font-bold mb-4">{item.title}</h3>
                                <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
                            </GlassCard>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── SECURITY & PRIVACY ──────────────────────────────────── */}
            <Section id="security">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-5xl mx-auto text-center">

                    <motion.div variants={fadeUp}>
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Security</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-6">
                            Your Data. <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Protected.</span> Always.
                        </h2>
                        <p className="text-gray-400 text-lg max-w-xl mx-auto mb-16">
                            Privacy-first architecture with enterprise-grade security at every layer.
                        </p>
                    </motion.div>

                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[
                            { icon: Lock, text: 'End-to-end secure API communication' },
                            { icon: Shield, text: 'JWT-based authentication' },
                            { icon: Eye, text: 'No direct exposure to AI providers' },
                            { icon: BadgeCheck, text: 'Privacy-first architecture' },
                        ].map((item, i) => (
                            <motion.div key={i} variants={fadeUp} custom={i}
                                className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] flex flex-col items-center gap-4">
                                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                                    <item.icon className="w-6 h-6 text-cyan-400" />
                                </div>
                                <span className="text-sm font-medium text-gray-300 text-center">{item.text}</span>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── CROSS-PLATFORM ───────────────────────────────────────── */}
            <Section className="bg-white/[0.01]">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-4xl mx-auto text-center">

                    <motion.div variants={fadeUp}>
                        <p className="text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4">Availability</p>
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-16">
                            One System.<br /><span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Everywhere.</span>
                        </h2>
                    </motion.div>

                    <div className="grid sm:grid-cols-3 gap-6">
                        {[
                            { icon: Globe, label: 'Web App', tech: 'React + Vite' },
                            { icon: Smartphone, label: 'Mobile App', tech: 'Flutter' },
                            { icon: Cloud, label: 'Cloud Backend', tech: 'FastAPI + RAG' },
                        ].map((item, i) => (
                            <GlassCard key={i} className="p-8 text-center">
                                <item.icon className="w-10 h-10 text-cyan-400 mx-auto mb-4" />
                                <h3 className="text-lg font-bold mb-1">{item.label}</h3>
                                <p className="text-gray-500 text-sm">{item.tech}</p>
                            </GlassCard>
                        ))}
                    </div>
                </motion.div>
            </Section>

            {/* ── FINAL CTA ───────────────────────────────────────────── */}
            <Section>
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }}
                    variants={stagger} className="max-w-3xl mx-auto text-center relative">

                    {/* Glow */}
                    <div className="absolute inset-0 -z-10">
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-cyan-500/10 rounded-full blur-[120px]" />
                    </div>

                    <motion.div variants={fadeUp}>
                        <Sparkles className="w-8 h-8 text-cyan-400 mx-auto mb-6" />
                        <h2 className="text-4xl md:text-6xl font-black tracking-tight mb-6">
                            Start Your AI-Powered<br />
                            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                                Medical Experience
                            </span>
                        </h2>
                        <p className="text-gray-400 text-lg mb-10 max-w-lg mx-auto">
                            Sign in to access personalized diagnostics, reports, and insights.
                        </p>
                    </motion.div>

                    <motion.div variants={fadeUp} className="flex flex-wrap justify-center gap-4">
                        <button onClick={() => navigate('/login')}
                            className="group px-10 py-4 text-base font-bold bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl hover:shadow-[0_8px_40px_rgba(0,212,255,0.3)] transition-all flex items-center gap-2">
                            Login <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button onClick={() => navigate('/register')}
                            className="px-10 py-4 text-base font-bold border border-white/10 rounded-2xl text-gray-300 hover:bg-white/5 hover:border-white/20 transition-all">
                            Create Account
                        </button>
                    </motion.div>
                </motion.div>
            </Section>

            {/* ── FOOTER ──────────────────────────────────────────────── */}
            <footer className="border-t border-white/5 py-12 px-6">
                <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
                            <Activity className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-sm font-bold tracking-wider">MedRAG</span>
                        <span className="text-xs text-gray-600">© {new Date().getFullYear()}</span>
                    </div>
                    <div className="flex gap-8 text-xs text-gray-500">
                        <a href="#" className="hover:text-gray-300 transition-colors">About</a>
                        <a href="#" className="hover:text-gray-300 transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-gray-300 transition-colors">Terms</a>
                        <a href="#" className="hover:text-gray-300 transition-colors">Contact</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
