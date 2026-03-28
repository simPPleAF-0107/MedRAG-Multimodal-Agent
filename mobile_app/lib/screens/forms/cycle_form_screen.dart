import 'package:flutter/material.dart';
import '../../utils/ux_utils.dart';

class CycleFormScreen extends StatefulWidget {
  const CycleFormScreen({super.key});

  @override
  State<CycleFormScreen> createState() => _CycleFormScreenState();
}

class _CycleFormScreenState extends State<CycleFormScreen> {
  DateTime? _selectedDate;
  String _flowIntensity = 'Light';
  double _crampsSeverity = 3.0;
  final TextEditingController _symptomsController = TextEditingController();

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
    }
  }

  void _submit() {
    FocusScope.of(context).unfocus();
    if (_selectedDate == null) {
      UxUtils.showToast(context, 'Please select a start date', isError: true);
      return;
    }
    UxUtils.hapticMedium();
    UxUtils.showToast(context, 'Cycle logged successfully!');
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reproductive Timeline')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Log Physiological Cycles', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 32),
            InkWell(
              onTap: () => _selectDate(context),
              child: InputDecorator(
                decoration: const InputDecoration(
                  labelText: 'Cycle Start Date',
                  prefixIcon: Icon(Icons.calendar_today),
                ),
                child: Text(
                  _selectedDate == null ? 'Select Date' : '${_selectedDate!.toLocal()}'.split(' ')[0],
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
            ),
            const SizedBox(height: 24),
            DropdownButtonFormField<String>(
              initialValue: _flowIntensity,
              decoration: const InputDecoration(labelText: 'Flow Intensity'),
              items: ['Spotting', 'Light', 'Medium', 'Heavy', 'Abnormal'].map((String value) {
                return DropdownMenuItem<String>(value: value, child: Text(value));
              }).toList(),
              onChanged: (newValue) => setState(() => _flowIntensity = newValue!),
            ),
            const SizedBox(height: 32),
            Text('Cramps/Pain Severity: ${_crampsSeverity.toInt()}/10', style: Theme.of(context).textTheme.titleSmall),
            Slider(
              value: _crampsSeverity,
              min: 0, max: 10, divisions: 10,
              activeColor: Colors.pinkAccent,
              onChanged: (val) {
                UxUtils.hapticLight();
                setState(() => _crampsSeverity = val);
              },
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _symptomsController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Associated Symptoms (e.g. headaches, fatigue)',
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 48),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Log Cycle Timeline'),
              ),
            )
          ],
        ),
      ),
    );
  }
}
