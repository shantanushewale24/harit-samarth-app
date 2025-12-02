export type Language = 'en' | 'hi' | 'mr';

export const translations: Record<Language, Record<string, string>> = {
  en: {
    // Navbar
    'nav.home': 'Home',
    'nav.soilHealth': 'Soil Health',
    'nav.crops': 'Crops',
    'nav.hardware': 'Hardware',
    'nav.subsidies': 'Subsidies',
    'nav.language': 'Language',
    
    // Hero
    'hero.title': 'Smart Farming for Better Harvests',
    'hero.subtitle': 'AI-powered soil analysis and crop recommendations',
    'hero.cta': 'Get Started',
    
    // Soil Health
    'soil.title': 'Soil Health Dashboard',
    'soil.subtitle': 'Real-time soil analysis with educational insights',
    'soil.overview': 'Overview',
    'soil.charts': 'Charts',
    'soil.learn': 'Learn',
    'soil.microbial': 'Microbial',
    'soil.metrics': 'Metrics',
    'soil.tips': 'Tips',
    'soil.nextReading': 'Next Reading In',
    'soil.lastUpdate': 'Last Update',
    'soil.overallHealth': 'Overall Health',
    'soil.status': 'Status',
    'soil.microbialHealth': 'Microbial Health',
    'soil.quickStatus': 'Quick Status',
    'soil.anomalous': 'Anomalous',
    'soil.criticalFactors': 'Critical Factors',
    'soil.anomalyScore': 'Anomaly Score',
    'soil.nutrientLevels': 'Nutrient Levels',
    'soil.physicalProperties': 'Physical Properties',
    'soil.biologicalProperties': 'Biological Properties',
    'soil.nitrogen': 'Nitrogen (N)',
    'soil.phosphorus': 'Phosphorus (P)',
    'soil.potassium': 'Potassium (K)',
    'soil.ph': 'pH Level',
    'soil.moisture': 'Moisture Content',
    'soil.temperature': 'Soil Temperature',
    'soil.co2': 'CO2 Level (Microbial Respiration)',
    'soil.microbialIndex': 'Microbial Health Index',
    'soil.recommendedActions': 'Actionable Recommendations',
    'soil.areasNeedingAttention': 'Areas needing attention',
    'soil.allOptimal': 'All parameters are within optimal ranges. Maintain current practices!',
    
    // Crops
    'crops.title': 'Crop Recommendation System',
    'crops.subtitle': 'Get AI-powered crop suggestions based on your soil',
    
    // Hardware
    'hardware.title': 'Smart Sensor Hardware',
    'hardware.subtitle': 'IoT devices for real-time soil monitoring',
    
    // Subsidies
    'subsidies.title': 'Government Subsidies',
    'subsidies.subtitle': 'Find and apply for available agricultural subsidies',
  },
  hi: {
    // Navbar
    'nav.home': 'होम',
    'nav.soilHealth': 'मिट्टी स्वास्थ्य',
    'nav.crops': 'फसलें',
    'nav.hardware': 'हार्डवेयर',
    'nav.subsidies': 'सब्सिडी',
    'nav.language': 'भाषा',
    
    // Hero
    'hero.title': 'बेहतर फसलों के लिए स्मार्ट खेती',
    'hero.subtitle': 'AI-संचालित मिट्टी विश्लेषण और फसल सुझाव',
    'hero.cta': 'शुरुआत करें',
    
    // Soil Health
    'soil.title': 'मिट्टी स्वास्थ्य डैशबोर्ड',
    'soil.subtitle': 'शिक्षात्मक अंतर्दृष्टि के साथ वास्तविक समय मिट्टी विश्लेषण',
    'soil.overview': 'अवलोकन',
    'soil.charts': 'चार्ट',
    'soil.learn': 'सीखें',
    'soil.microbial': 'सूक्ष्मजीव',
    'soil.metrics': 'मेट्रिक्स',
    'soil.tips': 'सुझाव',
    'soil.nextReading': 'अगली रीडिंग में',
    'soil.lastUpdate': 'अंतिम अपडेट',
    'soil.overallHealth': 'समग्र स्वास्थ्य',
    'soil.status': 'स्थिति',
    'soil.microbialHealth': 'सूक्ष्मजीव स्वास्थ्य',
    'soil.quickStatus': 'त्वरित स्थिति',
    'soil.anomalous': 'विसंगत',
    'soil.criticalFactors': 'महत्वपूर्ण कारक',
    'soil.anomalyScore': 'विसंगति स्कोर',
    'soil.nutrientLevels': 'पोषक स्तर',
    'soil.physicalProperties': 'भौतिक गुण',
    'soil.biologicalProperties': 'जैविक गुण',
    'soil.nitrogen': 'नाइट्रोजन (N)',
    'soil.phosphorus': 'फास्फोरस (P)',
    'soil.potassium': 'पोटेशियम (K)',
    'soil.ph': 'पीएच स्तर',
    'soil.moisture': 'नमी सामग्री',
    'soil.temperature': 'मिट्टी का तापमान',
    'soil.co2': 'CO2 स्तर (सूक्ष्मजीव श्वसन)',
    'soil.microbialIndex': 'सूक्ष्मजीव स्वास्थ्य सूचकांक',
    'soil.recommendedActions': 'कार्रवाई योग्य सिफारिशें',
    'soil.areasNeedingAttention': 'ध्यान देने योग्य क्षेत्र',
    'soil.allOptimal': 'सभी पैरामीटर इष्टतम सीमा के भीतर हैं। वर्तमान प्रथाओं को बनाए रखें!',
    
    // Crops
    'crops.title': 'फसल सुझाव प्रणाली',
    'crops.subtitle': 'अपनी मिट्टी के आधार पर AI-संचालित फसल सुझाव प्राप्त करें',
    
    // Hardware
    'hardware.title': 'स्मार्ट सेंसर हार्डवेयर',
    'hardware.subtitle': 'वास्तविक समय मिट्टी निगरानी के लिए IoT उपकरण',
    
    // Subsidies
    'subsidies.title': 'सरकारी सब्सिडी',
    'subsidies.subtitle': 'उपलब्ध कृषि सब्सिडी खोजें और आवेदन करें',
  },
  mr: {
    // Navbar
    'nav.home': 'होम',
    'nav.soilHealth': 'मातीची आरोग्य',
    'nav.crops': 'पिके',
    'nav.hardware': 'हार्डवेयर',
    'nav.subsidies': 'अनुदान',
    'nav.language': 'भाषा',
    
    // Hero
    'hero.title': 'चांगल्या पिकांसाठी स्मार्ट शेती',
    'hero.subtitle': 'AI-चालित मातीचे विश्लेषण आणि पिकांचे सुझाव',
    'hero.cta': 'सुरुवात करा',
    
    // Soil Health
    'soil.title': 'मातीची आरोग्य डॅशबोर्ड',
    'soil.subtitle': 'शैक्षणिक अंतर्दृष्टीसह रीअल-टाइम मातीचे विश्लेषण',
    'soil.overview': 'पूर्वावलोकन',
    'soil.charts': 'चार्ट',
    'soil.learn': 'शिका',
    'soil.microbial': 'सूक्ष्मजीव',
    'soil.metrics': 'मेट्रिक्स',
    'soil.tips': 'सुझाव',
    'soil.nextReading': 'पुढील वाचन',
    'soil.lastUpdate': 'शेवटची अपडेट',
    'soil.overallHealth': 'एकूण आरोग्य',
    'soil.status': 'स्थिती',
    'soil.microbialHealth': 'सूक्ष्मजीव आरोग्य',
    'soil.quickStatus': 'द्रुत स्थिती',
    'soil.anomalous': 'विसंगत',
    'soil.criticalFactors': 'महत्वपूर्ण घटक',
    'soil.anomalyScore': 'विसंगती स्कोर',
    'soil.nutrientLevels': 'पोषक स्तर',
    'soil.physicalProperties': 'शारीरिक गुणधर्म',
    'soil.biologicalProperties': 'जैविक गुणधर्म',
    'soil.nitrogen': 'नायट्रोजन (N)',
    'soil.phosphorus': 'फॉस्फरस (P)',
    'soil.potassium': 'पोटेशियम (K)',
    'soil.ph': 'pH स्तर',
    'soil.moisture': 'ओलावा सामग्री',
    'soil.temperature': 'मातीचे तापमान',
    'soil.co2': 'CO2 स्तर (सूक्ष्मजीव श्वसन)',
    'soil.microbialIndex': 'सूक्ष्मजीव आरोग्य निर्देशांक',
    'soil.recommendedActions': 'कार्यान्वयन योग्य शिफारशी',
    'soil.areasNeedingAttention': 'लक्ष देणे आवश्यक क्षेत्र',
    'soil.allOptimal': 'सर्व पॅरामीटर इष्टतम श्रेणीमध्ये आहेत। वर्तमान प्रथा कायम ठेवा!',
    
    // Crops
    'crops.title': 'पिकांच्या सुझाव प्रणाली',
    'crops.subtitle': 'आपल्या मातीच्या आधारे AI-चालित पिकांचे सुझाव मिळवा',
    
    // Hardware
    'hardware.title': 'स्मार्ट सेंसर हार्डवेयर',
    'hardware.subtitle': 'रीअल-टाइम मातीच्या निरीक्षणासाठी IoT उपकरणे',
    
    // Subsidies
    'subsidies.title': 'सरकारी अनुदान',
    'subsidies.subtitle': 'उपलब्ध कृषी अनुदान शोधा आणि अर्ज करा',
  }
};

export const getTranslation = (key: string, language: Language): string => {
  return translations[language][key] || translations['en'][key] || key;
};
