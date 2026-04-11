import React, { useState, useEffect } from 'react';
import { Utensils, Send, Sparkles, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getTrackerSuggestion } from '../services/apiClient';
import toast from 'react-hot-toast';

const MealPlanner = () => {
    const [meals, setMeals] = useState([]);
    const [mealType, setMealType] = useState('Breakfast');
    const [description, setDescription] = useState('');
    const [protein, setProtein] = useState('');
    const [carbs, setCarbs] = useState('');
    const [fats, setFats] = useState('');
    const [loading, setLoading] = useState(true);
    const [aiSuggestion, setAiSuggestion] = useState('');
    const [aiLoading, setAiLoading] = useState(false);

    useEffect(() => {
        setTimeout(() => {
            setMeals([
                { id: 1, type: 'Breakfast', description: 'Oatmeal with berries and nuts (Anti-inflammatory)', macros: { p: 15, c: 45, f: 12 }, timestamp: '2026-02-21T07:30:00Z' },
                { id: 2, type: 'Lunch', description: 'Grilled salmon salad with olive oil dressing (Omega-3 rich)', macros: { p: 35, c: 10, f: 22 }, timestamp: '2026-02-21T12:30:00Z' },
            ]);
            setLoading(false);
        }, 600);
    }, []);

    const handleLogSubmit = (e) => {
        e.preventDefault();
        if (!description) return;
        const newMeal = {
            id: Date.now(), type: mealType, description,
            macros: { p: protein ? parseInt(protein) : 0, c: carbs ? parseInt(carbs) : 0, f: fats ? parseInt(fats) : 0 },
            timestamp: new Date().toISOString(),
        };
        setMeals([newMeal, ...meals]);
        setDescription(''); setProtein(''); setCarbs(''); setFats('');
        toast.success('Meal logged successfully!');
    };

    const handleAISuggest = async () => {
        setAiLoading(true);
        try {
            const result = await getTrackerSuggestion('meal', meals.slice(0, 10));
            setAiSuggestion(result.suggestion || 'No suggestion available.');
        } catch { setAiSuggestion('Failed to generate suggestion.'); }
        setAiLoading(false);
    };

    // Calculate daily totals
    const todayMeals = meals.filter(m => new Date(m.timestamp).toDateString() === new Date().toDateString());
    const totalP = todayMeals.reduce((s, m) => s + (m.macros?.p || 0), 0);
    const totalC = todayMeals.reduce((s, m) => s + (m.macros?.c || 0), 0);
    const totalF = todayMeals.reduce((s, m) => s + (m.macros?.f || 0), 0);
    const totalCal = Math.round(totalP * 4 + totalC * 4 + totalF * 9);

    return (
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-up">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                    <div className="p-3 rounded-xl" style={{ background: 'rgba(58,12,163,0.08)' }}>
                        <Utensils size={24} style={{ color: 'var(--primary)' }} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Nutrition Tracker</h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>Log meals and get AI-powered nutrition plans</p>
                    </div>
                </div>
                <button onClick={handleAISuggest} disabled={aiLoading}
                    className="btn-primary flex items-center gap-2 text-sm disabled:opacity-50">
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    {aiLoading ? 'Generating...' : 'AI Meal Plan'}
                </button>
            </div>

            {/* Daily Summary */}
            <div className="grid grid-cols-4 gap-4">
                {[
                    { label: 'Calories', value: `${totalCal}`, unit: 'kcal', color: 'var(--primary)' },
                    { label: 'Protein', value: `${totalP}`, unit: 'g', color: 'var(--secondary)' },
                    { label: 'Carbs', value: `${totalC}`, unit: 'g', color: 'var(--success)' },
                    { label: 'Fats', value: `${totalF}`, unit: 'g', color: 'var(--warning)' },
                ].map((stat) => (
                    <div key={stat.label} className="bento-card p-4 text-center">
                        <p className="label-caps mb-1">{stat.label}</p>
                        <p className="text-2xl font-bold" style={{ color: stat.color }}>{stat.value}<span className="text-sm font-normal ml-1" style={{ color: 'var(--text-muted)' }}>{stat.unit}</span></p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Log Form */}
                <div className="bento-card p-6">
                    <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Log Meal</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Meal Type</label>
                            <select value={mealType} onChange={(e) => setMealType(e.target.value)} className="glass-input">
                                <option>Breakfast</option><option>Lunch</option><option>Dinner</option><option>Snack</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Description</label>
                            <textarea rows="2" className="glass-input resize-none" placeholder="e.g. 2 eggs, avocado toast..." value={description} onChange={(e) => setDescription(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Macros (g) — P / C / F</label>
                            <div className="grid grid-cols-3 gap-2">
                                <input type="number" placeholder="Pro" className="glass-input text-center" value={protein} onChange={(e) => setProtein(e.target.value)} />
                                <input type="number" placeholder="Carb" className="glass-input text-center" value={carbs} onChange={(e) => setCarbs(e.target.value)} />
                                <input type="number" placeholder="Fat" className="glass-input text-center" value={fats} onChange={(e) => setFats(e.target.value)} />
                            </div>
                        </div>
                        <button type="submit" disabled={!description} className="btn-primary w-full flex justify-center items-center disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                {/* Meal History */}
                <div className="lg:col-span-2 bento-card p-6 flex flex-col" style={{ maxHeight: 520 }}>
                    <h3 className="font-semibold mb-4 pb-2" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }}>Recent Meals</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                        {loading ? (
                            <p className="text-sm animate-pulse" style={{ color: 'var(--primary)' }}>Loading logs...</p>
                        ) : meals.map(meal => (
                            <div key={meal.id} className="p-4 rounded-xl" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{meal.type}</span>
                                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{new Date(meal.timestamp).toLocaleString()}</span>
                                </div>
                                <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>{meal.description}</p>
                                {meal.macros && (
                                    <div className="flex space-x-4 py-2 px-3 rounded-lg justify-center" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                                        <div className="text-center"><span className="text-xs block" style={{ color: 'var(--text-muted)' }}>Protein</span><span className="text-sm font-bold" style={{ color: 'var(--secondary)' }}>{meal.macros.p}g</span></div>
                                        <div className="text-center"><span className="text-xs block" style={{ color: 'var(--text-muted)' }}>Carbs</span><span className="text-sm font-bold" style={{ color: 'var(--success)' }}>{meal.macros.c}g</span></div>
                                        <div className="text-center"><span className="text-xs block" style={{ color: 'var(--text-muted)' }}>Fats</span><span className="text-sm font-bold" style={{ color: 'var(--warning)' }}>{meal.macros.f}g</span></div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Suggestion Panel */}
            <AnimatePresence>
                {aiSuggestion && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="ai-panel">
                        <div className="ai-panel-header">
                            <Sparkles size={16} /> AI-Generated Meal Plan
                        </div>
                        <div className="prose prose-sm max-w-none" style={{ color: 'var(--text-secondary)' }}>
                            {aiSuggestion.split('\n').map((line, i) => {
                                if (line.startsWith('## ')) return <h2 key={i} className="text-lg font-bold mt-4 mb-2" style={{ color: 'var(--text-primary)' }}>{line.replace('## ', '')}</h2>;
                                if (line.startsWith('### ')) return <h3 key={i} className="text-base font-semibold mt-3 mb-1" style={{ color: 'var(--primary)' }}>{line.replace('### ', '')}</h3>;
                                if (line.startsWith('- ')) return <p key={i} className="ml-4 mb-0.5">• {line.replace('- ', '')}</p>;
                                if (line.trim() === '') return <br key={i} />;
                                return <p key={i} className="mb-1">{line}</p>;
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default MealPlanner;
