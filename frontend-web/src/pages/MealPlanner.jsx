import React, { useState, useEffect } from 'react';
import { Utensils, Send } from 'lucide-react';

const MealPlanner = () => {
    const [meals, setMeals] = useState([]);
    const [mealType, setMealType] = useState("Breakfast");
    const [description, setDescription] = useState("");
    const [loading, setLoading] = useState(true);

    // Simulating fetching meal history or recommendation plans
    useEffect(() => {
        setTimeout(() => {
            setMeals([
                { id: 1, type: 'Breakfast', description: 'Oatmeal with berries and nuts (Anti-inflammatory)', timestamp: '2026-02-21T07:30:00Z' },
                { id: 2, type: 'Lunch', description: 'Grilled salmon salad with olive oil dressing (Omega-3 rich)', timestamp: '2026-02-21T12:30:00Z' }
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
            timestamp: new Date().toISOString()
        };
        setMeals([newMeal, ...meals]);
        setDescription("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-brand-100 text-brand-600 rounded-xl">
                    <Utensils size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Personalized Meal Strategy & Log</h1>
                    <p className="text-slate-500 mt-1">Logs dietary inputs and compares against engine-recommended nutrition plans.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="font-semibold text-slate-800 mb-4">Log Patient Meal</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Meal Type</label>
                            <select
                                value={mealType} onChange={(e) => setMealType(e.target.value)}
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-brand-500 outline-none bg-white"
                            >
                                <option>Breakfast</option>
                                <option>Lunch</option>
                                <option>Dinner</option>
                                <option>Snack</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Description / Notes</label>
                            <textarea
                                rows="3"
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-brand-500 outline-none resize-none"
                                placeholder="e.g. 2 eggs, avocado toast..."
                                value={description} onChange={(e) => setDescription(e.target.value)}
                            />
                        </div>
                        <button type="submit" disabled={!description} className="w-full bg-brand-600 hover:bg-brand-700 text-white font-medium py-2 rounded-lg transition flex justify-center items-center disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 overflow-hidden flex flex-col h-[400px]">
                    <h3 className="font-semibold text-slate-800 mb-4 border-b pb-2">Recent Diet History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                        {loading ? (
                            <p className="text-slate-500 animate-pulse text-sm">Loading logs...</p>
                        ) : meals.length > 0 ? (
                            meals.map(meal => (
                                <div key={meal.id} className="p-4 bg-slate-50 border border-slate-100 rounded-lg flex justify-between items-start">
                                    <div>
                                        <span className="text-sm font-semibold text-slate-800 block">{meal.type}</span>
                                        <span className="text-xs text-slate-400 block mb-1">
                                            {new Date(meal.timestamp).toLocaleString()}
                                        </span>
                                        <p className="text-sm text-slate-700">{meal.description}</p>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-slate-500 text-sm">No meals logged yet.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MealPlanner;
