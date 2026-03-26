import React, { useState, useEffect } from 'react';
import { Utensils, Send } from 'lucide-react';

const MealPlanner = () => {
    const [meals, setMeals] = useState([]);
    const [mealType, setMealType] = useState("Breakfast");
    const [description, setDescription] = useState("");
    const [protein, setProtein] = useState("");
    const [carbs, setCarbs] = useState("");
    const [fats, setFats] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setTimeout(() => {
            setMeals([
                { id: 1, type: 'Breakfast', description: 'Oatmeal with berries and nuts (Anti-inflammatory)', macros: { p: 15, c: 45, f: 12 }, timestamp: '2026-02-21T07:30:00Z' },
                { id: 2, type: 'Lunch', description: 'Grilled salmon salad with olive oil dressing (Omega-3 rich)', macros: { p: 35, c: 10, f: 22 }, timestamp: '2026-02-21T12:30:00Z' }
            ]);
            setLoading(false);
        }, 600);
    }, []);

    const handleLogSubmit = (e) => {
        e.preventDefault();
        if (!description) return;
        const newMeal = {
            id: Date.now(),
            type: mealType,
            description,
            macros: {
                p: protein ? parseInt(protein) : 0,
                c: carbs ? parseInt(carbs) : 0,
                f: fats ? parseInt(fats) : 0
            },
            timestamp: new Date().toISOString()
        };
        setMeals([newMeal, ...meals]);
        setDescription(""); setProtein(""); setCarbs(""); setFats("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in font-sans">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-brand-500/20 text-brand-500 rounded-xl shadow-neon">
                    <Utensils size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Personalized Nutrition Log</h1>
                    <p className="text-slate-400 mt-1">Logs dietary inputs and macros against engine-recommended nutrition plans.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface rounded-xl border border-slate-800 shadow-xl p-6">
                    <h3 className="font-semibold text-white mb-4">Log Patient Meal</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Meal Type</label>
                            <select value={mealType} onChange={(e) => setMealType(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-brand-500 outline-none">
                                <option>Breakfast</option><option>Lunch</option><option>Dinner</option><option>Snack</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Description / Notes</label>
                            <textarea rows="2" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-brand-500 outline-none resize-none" placeholder="e.g. 2 eggs, avocado toast..." value={description} onChange={(e) => setDescription(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Macros (g) [P / C / F]</label>
                            <div className="grid grid-cols-3 gap-2">
                                <input type="number" placeholder="Pro" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white text-center focus:border-brand-500 outline-none" value={protein} onChange={(e) => setProtein(e.target.value)} />
                                <input type="number" placeholder="Carb" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white text-center focus:border-brand-500 outline-none" value={carbs} onChange={(e) => setCarbs(e.target.value)} />
                                <input type="number" placeholder="Fat" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white text-center focus:border-brand-500 outline-none" value={fats} onChange={(e) => setFats(e.target.value)} />
                            </div>
                        </div>
                        <button type="submit" disabled={!description} className="w-full bg-brand-500 hover:bg-brand-400 text-deepSpace font-bold py-2.5 rounded-lg transition flex justify-center items-center disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-surface rounded-xl border border-slate-800 shadow-xl p-6 overflow-hidden flex flex-col h-[480px]">
                    <h3 className="font-semibold text-white mb-4 border-b border-slate-800 pb-2">Recent Diet History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
                        {loading ? <p className="text-brand-500 animate-pulse text-sm">Translating records...</p> : meals.map(meal => (
                            <div key={meal.id} className="p-4 bg-deepSpace border border-slate-800 rounded-lg flex justify-between items-start">
                                <div className="w-full">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-sm font-bold text-white block">{meal.type}</span>
                                        <span className="text-xs text-slate-500">{new Date(meal.timestamp).toLocaleString()}</span>
                                    </div>
                                    <p className="text-sm text-slate-300 mb-3">{meal.description}</p>
                                    
                                    {meal.macros && (
                                        <div className="flex space-x-4 bg-surface py-2 px-3 justify-center rounded-lg border border-slate-800">
                                            <div className="text-center"><span className="text-xs text-slate-500 block">Protein</span><span className="text-sm font-bold text-brand-500">{meal.macros.p}g</span></div>
                                            <div className="text-center"><span className="text-xs text-slate-500 block">Carbs</span><span className="text-sm font-bold text-brand-500">{meal.macros.c}g</span></div>
                                            <div className="text-center"><span className="text-xs text-slate-500 block">Fats</span><span className="text-sm font-bold text-brand-500">{meal.macros.f}g</span></div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MealPlanner;
