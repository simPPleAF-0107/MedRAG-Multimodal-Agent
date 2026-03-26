import 'package:flutter/material.dart';
import '../../utils/ux_utils.dart';

class MealFormScreen extends StatefulWidget {
  const MealFormScreen({super.key});

  @override
  State<MealFormScreen> createState() => _MealFormScreenState();
}

class _MealFormScreenState extends State<MealFormScreen> {
  final _mealDescController = TextEditingController();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatsController = TextEditingController();

  void _submit() {
    FocusScope.of(context).unfocus();
    if (_mealDescController.text.isEmpty) {
      UxUtils.showToast(context, 'Please describe your meal', isError: true);
      return;
    }
    UxUtils.hapticMedium();
    UxUtils.showToast(context, 'Dietary entry logged!');
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Meal Planner')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Track Dietary Considerations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 32),
            TextField(
              controller: _mealDescController,
              decoration: const InputDecoration(
                labelText: 'Meal Description',
                prefixIcon: Icon(Icons.restaurant_menu),
              ),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _caloriesController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Total Calories (kcal)',
                prefixIcon: Icon(Icons.local_fire_department_outlined),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(child: TextField(controller: _proteinController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Protein (g)'))),
                const SizedBox(width: 8),
                Expanded(child: TextField(controller: _carbsController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Carbs (g)'))),
                const SizedBox(width: 8),
                Expanded(child: TextField(controller: _fatsController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Fats (g)'))),
              ],
            ),
            const SizedBox(height: 48),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Log Meal Data'),
              ),
            )
          ],
        ),
      ),
    );
  }
}
