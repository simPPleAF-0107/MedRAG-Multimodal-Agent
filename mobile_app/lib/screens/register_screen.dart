import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/user_provider.dart';
import '../services/api_service.dart';
import '../utils/ux_utils.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  int _currentStep = 0;
  bool _isLoading = false;

  // Step 1: Personal
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _contactController = TextEditingController();
  final _passwordController = TextEditingController();
  DateTime? _dob;
  String? _gender;

  // Step 2: Vitals & Lifestyle
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  String? _smokingStatus;
  String? _drinkingStatus;
  final _lifestyleController = TextEditingController();

  // Step 3: Medical History
  final _conditionsController = TextEditingController();
  final _surgeriesController = TextEditingController();
  final _familyHistoryController = TextEditingController();
  final _allergiesController = TextEditingController();
  final _medicationsController = TextEditingController();
  final _physicianController = TextEditingController();

  int _calculateAge(DateTime birthDate) {
    DateTime currentDate = DateTime.now();
    int age = currentDate.year - birthDate.year;
    int month1 = currentDate.month;
    int month2 = birthDate.month;
    if (month2 > month1) {
      age--;
    } else if (month1 == month2) {
      int day1 = currentDate.day;
      int day2 = birthDate.day;
      if (day2 > day1) {
        age--;
      }
    }
    return age;
  }

  String _generatePatientId(String firstName, String lastName) {
    String firstInitial = firstName.isNotEmpty ? firstName[0].toUpperCase() : 'X';
    String lastInitial = lastName.isNotEmpty ? lastName[0].toUpperCase() : 'X';
    String randomDigits = (Random().nextInt(900000) + 100000).toString(); // 6 digits
    return '$firstInitial$lastInitial$randomDigits';
  }

  Future<void> _handleRegister() async {
    FocusScope.of(context).unfocus();
    
    // Minimum validation
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty || _firstNameController.text.isEmpty || _lastNameController.text.isEmpty) {
      UxUtils.showToast(context, 'Please fill at least your Name, Email, and Password.', isError: true);
      return;
    }

    UxUtils.hapticLight();
    setState(() => _isLoading = true);

    String patientId = _generatePatientId(_firstNameController.text.trim(), _lastNameController.text.trim());
    int? age = _dob != null ? _calculateAge(_dob!) : null;

    try {
      final res = await ApiService().register(
        patientId: patientId,
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        email: _emailController.text.trim(),
        contactNumber: _contactController.text.trim(),
        password: _passwordController.text,
        dob: _dob != null ? '${_dob!.toLocal()}'.split(' ')[0] : '',
        age: age?.toString() ?? '',
        gender: _gender ?? '',
        height: _heightController.text.trim(),
        weight: _weightController.text.trim(),
        smokingStatus: _smokingStatus ?? '',
        drinkingStatus: _drinkingStatus ?? '',
        lifestyleOther: _lifestyleController.text.trim(),
        pastConditions: _conditionsController.text.trim(),
        surgeries: _surgeriesController.text.trim(),
        familyHistory: _familyHistoryController.text.trim(),
        allergies: _allergiesController.text.trim(),
        medications: _medicationsController.text.trim(),
        physicianName: _physicianController.text.trim(),
      );
      
      if (mounted && res['status'] == 'success') {
         UxUtils.hapticMedium();
         UxUtils.showToast(context, 'Registration Successful! Logging in as $patientId...');
         
         // Auto-login the new user
         context.read<UserProvider>().setUser(res['user_id'].toString(), res['email'], res['role']);
         Navigator.of(context).popUntil((route) => route.isFirst);
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Registration Failed: \n${e.toString()}', isError: true);
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _dob ?? DateTime(2000),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _dob) {
      setState(() => _dob = picked);
    }
  }

  List<Step> _getSteps() {
    return [
      Step(
        title: const Text('Personal Details'),
        subtitle: const Text('Basic Identification'),
        isActive: _currentStep >= 0,
        state: _currentStep > 0 ? StepState.complete : StepState.indexed,
        content: Column(
          children: [
            Row(
              children: [
                Expanded(child: TextField(controller: _firstNameController, decoration: const InputDecoration(labelText: 'First Name', prefixIcon: Icon(Icons.person_outline)))),
                const SizedBox(width: 8),
                Expanded(child: TextField(controller: _lastNameController, decoration: const InputDecoration(labelText: 'Last Name'))),
              ],
            ),
            const SizedBox(height: 16),
            TextField(controller: _emailController, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email Address', prefixIcon: Icon(Icons.email_outlined))),
            const SizedBox(height: 16),
            TextField(controller: _contactController, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Contact Number', prefixIcon: Icon(Icons.phone_outlined))),
            const SizedBox(height: 16),
            TextField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline))),
            const SizedBox(height: 16),
            InkWell(
              onTap: () => _selectDate(context),
              child: InputDecorator(
                decoration: const InputDecoration(labelText: 'Date of Birth', prefixIcon: Icon(Icons.cake_outlined)),
                child: Text(_dob == null ? 'Select Date' : '${_dob!.toLocal()}'.split(' ')[0]),
              ),
            ),
            if (_dob != null) Padding(
              padding: const EdgeInsets.only(top: 8.0, left: 12),
              child: Align(alignment: Alignment.centerLeft, child: Text('Calculated Age: ${_calculateAge(_dob!)} years', style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold))),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _gender,
              decoration: const InputDecoration(labelText: 'Sex / Gender', prefixIcon: Icon(Icons.transgender_outlined)),
              items: ['Male', 'Female', 'Non-Binary', 'Other', 'Prefer Not to Say'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
              onChanged: (val) => setState(() => _gender = val),
            ),
          ],
        ),
      ),
      Step(
        title: const Text('Vitals & Lifestyle'),
        subtitle: const Text('Physical metrics & habits'),
        isActive: _currentStep >= 1,
        state: _currentStep > 1 ? StepState.complete : StepState.indexed,
        content: Column(
          children: [
            Row(
              children: [
                Expanded(child: TextField(controller: _heightController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height (cm)'))),
                const SizedBox(width: 8),
                Expanded(child: TextField(controller: _weightController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Weight (kg)'))),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _smokingStatus,
              decoration: const InputDecoration(labelText: 'Smoking Status'),
              items: ['Never Smoked', 'Former Smoker', 'Current Smoker', 'Occasional'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
              onChanged: (val) => setState(() => _smokingStatus = val),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _drinkingStatus,
              decoration: const InputDecoration(labelText: 'Alcohol Consumption'),
              items: ['Non-Drinker', 'Occasional', 'Regular', 'Heavy'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
              onChanged: (val) => setState(() => _drinkingStatus = val),
            ),
            const SizedBox(height: 16),
            TextField(controller: _lifestyleController, maxLines: 2, decoration: const InputDecoration(labelText: 'Other Lifestyle Activities (e.g. daily exercise)', alignLabelWithHint: true)),
          ],
        ),
      ),
      Step(
        title: const Text('Medical History'),
        subtitle: const Text('Past conditions & physicians'),
        isActive: _currentStep >= 2,
        content: Column(
          children: [
            TextField(controller: _conditionsController, maxLines: 2, decoration: const InputDecoration(labelText: 'Past Medical Conditions', alignLabelWithHint: true)),
            const SizedBox(height: 16),
            TextField(controller: _surgeriesController, maxLines: 2, decoration: const InputDecoration(labelText: 'Surgical History', alignLabelWithHint: true)),
            const SizedBox(height: 16),
            TextField(controller: _familyHistoryController, maxLines: 2, decoration: const InputDecoration(labelText: 'Family Medical History', alignLabelWithHint: true)),
            const SizedBox(height: 16),
            TextField(controller: _allergiesController, maxLines: 2, decoration: const InputDecoration(labelText: 'Allergies (Drug, Food, Environmental)', alignLabelWithHint: true)),
            const SizedBox(height: 16),
            TextField(controller: _medicationsController, maxLines: 2, decoration: const InputDecoration(labelText: 'Current Medications', alignLabelWithHint: true)),
            const SizedBox(height: 16),
            TextField(controller: _physicianController, decoration: const InputDecoration(labelText: 'Attending Physician\'s Name', prefixIcon: Icon(Icons.medical_services_outlined))),
          ],
        ),
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Patient Registration'),
      ),
      body: SafeArea(
        child: _isLoading 
        ? Center(child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 24),
              Text('Generating Secure Patient Profile...', style: Theme.of(context).textTheme.titleMedium),
            ],
          ))
        : Stepper(
            type: StepperType.vertical,
            currentStep: _currentStep,
            physics: const ClampingScrollPhysics(),
            onStepContinue: () {
              if (_currentStep < _getSteps().length - 1) {
                setState(() => _currentStep += 1);
              } else {
                _handleRegister();
              }
            },
            onStepCancel: () {
              if (_currentStep > 0) {
                setState(() => _currentStep -= 1);
              } else {
                Navigator.of(context).pop();
              }
            },
            controlsBuilder: (context, details) {
              final isLastStep = _currentStep == _getSteps().length - 1;
              return Padding(
                padding: const EdgeInsets.only(top: 24.0),
                child: Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: ElevatedButton(
                        onPressed: details.onStepContinue,
                        child: Text(isLastStep ? 'Complete Registration' : 'Next'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 1,
                      child: OutlinedButton(
                        onPressed: details.onStepCancel,
                        child: Text(_currentStep == 0 ? 'Cancel' : 'Back'),
                      ),
                    ),
                  ],
                ),
              );
            },
            steps: _getSteps(),
          ),
      ),
    );
  }
}
