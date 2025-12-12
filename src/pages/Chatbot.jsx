import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FaRobot, FaUser, FaPaperPlane } from 'react-icons/fa';
import './Chatbot.css';

const Chatbot = () => {
    const [messages, setMessages] = useState([
        {
            sender: 'bot',
            text: 'Namaste! I am your Advanced AI Agriculture Assistant. I can help with:\n\n🌿 Crop Diseases\n💰 Market Prices\n💧 Irrigation Advice\n📜 Government Schemes\n\nHow can I assist you today?'
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('English'); // Language State

    // UI Translations
    const translations = {
        English: {
            title: "🤖 Agri-Assist AI",
            subtitle: "Expert farming advice 24/7",
            placeholder: "Ask about your farm...",
            suggestions: [
                "Why are my tomato leaves yellow?",
                "Price of onion in Maharashtra?",
                "Best fertilizer for Rice?",
                "Details of PM Kisan scheme"
            ],
            welcome: "Namaste! I am your Advanced AI Agriculture Assistant. I can help with:\n\n🌿 Crop Diseases\n💰 Market Prices\n💧 Irrigation Advice\n📜 Government Schemes\n\nHow can I assist you today?"
        },
        Kannada: {
            title: "🤖 ಕೃಷಿ-ಸಹಾಯಕ AI",
            subtitle: "ತಜ್ಞ ಕೃಷಿ ಸಲಹೆ 24/7",
            placeholder: "ನಿಮ್ಮ ಕೃಷಿಯ ಬಗ್ಗೆ ಕೇಳಿ...",
            suggestions: [
                "ಟೊಮೆಟೊ ಎಲೆಗಳು ಏಕೆ ಹಳದಿಯಾಗುತ್ತಿವೆ?",
                "ಮಹಾರಾಷ್ಟ್ರದಲ್ಲಿ ಈರುಳ್ಳಿ ಬೆಲೆ?",
                "ಭತ್ತಕ್ಕೆ ಉತ್ತಮ ಗೊಬ್ಬರ ಯಾವುದು?",
                "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆಯ ವಿವರಗಳು"
            ],
            welcome: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಸುಧಾರಿತ AI ಕೃಷಿ ಸಹಾಯಕ. ನಾನು ಇವುಗಳಿಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n\n🌿 ಬೆಳೆ ರೋಗಗಳು\n💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು\n💧 ನೀರಾವರಿ ಸಲಹೆ\n📜 ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು\n\nನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
        },
        Hindi: {
            title: "🤖 कृषि-सहायक AI",
            subtitle: "विशेषज्ञ कृषि सलाह 24/7",
            placeholder: "अपनी खेती के बारे में पूछें...",
            suggestions: [
                "मेरे टमाटर के पत्ते पीले क्यों हो रहे हैं?",
                "महाराष्ट्र में प्याज का भाव?",
                "चावल के लिए सबसे अच्छा उर्वरक?",
                "पीएम किसान योजना का विवरण"
            ],
            welcome: "नमस्ते! मैं आपका उन्नत AI कृषि सहायक हूँ। मैं मदद कर सकता हूँ:\n\n🌿 फसल रोग\n💰 बाजार मूल्य\n💧 सिंचाई सलाह\n📜 सरकारी योजनाएं\n\nआज मैं आपकी कैसे सहायता कर सकता हूँ?"
        },
        Telugu: {
            title: "🤖 అగ్రి-అసిస్ట్ AI",
            subtitle: "నిపుణుల వ్యవసాయ సలహా 24/7",
            placeholder: "మీ పొలం గురించి అడగండి...",
            suggestions: [
                "నా టమోటా ఆకులు ఎందుకు పసుపు రంగులోకి మారుతున్నాయి?",
                "మహారాష్ట్రలో ఉల్లిపాయ ధర?",
                "వరికి ఉత్తమ ఎరువులు?",
                "PM కిసాన్ పథకం వివరాలు"
            ],
            welcome: "నమస్కారం! నేను మీ అడ్వాన్స్‌డ్ AI అగ్రి అసిస్టెంట్‌ని. నేను సహాయం చేయగలను:\n\n🌿 పంట వ్యాధులు\n💰 మార్కెట్ ధరలు\n💧 నీటిపారుదల సలహా\n📜 ప్రభుత్వ పథకాలు\n\nనేను మీకు ఎలా సహాయం చేయగలను?"
        },
        Tamil: {
            title: "🤖 அக்ரி-அசிஸ்ட் AI",
            subtitle: "நிபுணர் விவசாய ஆலோசனை 24/7",
            placeholder: "உங்கள் பண்ணையைப் பற்றி கேளுங்கள்...",
            suggestions: [
                "தக்காளி இலைகள் ஏன் மஞ்சளாகின்றன?",
                "மகாராஷ்டிராவில் வெங்காயத்தின் விலை?",
                "நெல்லுக்கு சிறந்த உரம் எது?",
                "பிஎம் கிசான் திட்டத்தின் விவரங்கள்"
            ],
            welcome: "வணக்கம்! நான் உங்கள் மேம்பட்ட AI விவசாய உதவியாளர். நான் உதவ முடியும்:\n\n🌿 பயிர் நோய்கள்\n💰 சந்தை விலைகள்\n💧 நீர்ப்பாசன ஆலோசனை\n📜 அரசு திட்டங்கள்\n\nஇன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
        }
    };

    // Get current text based on selection
    const t = translations[selectedLanguage] || translations['English'];

    // Update Welcome Message when language changes (if it's the only message)
    useEffect(() => {
        setMessages(prev => {
            if (prev.length === 1 && prev[0].sender === 'bot') {
                return [{ sender: 'bot', text: t.welcome }];
            }
            return prev;
        });
    }, [selectedLanguage, t.welcome]); // Added t.welcome to dependency array

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Include language in request
            const res = await axios.post('http://localhost:5000/chatbot', {
                question: userMsg.text,
                language: selectedLanguage
            });
            const botMsg = { sender: 'bot', text: res.data.answer };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I'm having trouble connecting to the server. Please try again later." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="chatbot-header">
                <div>
                    <h1>{t.title}</h1>
                    <p>{t.subtitle}</p>
                </div>
                {/* Language Dropdown */}
                <select
                    className="language-selector"
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    style={{ padding: '5px', borderRadius: '5px' }}
                >
                    <option value="English">English</option>
                    <option value="Kannada">Kannada</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Telugu">Telugu</option>
                    <option value="Tamil">Tamil</option>
                </select>
            </div>

            <div className="chat-window">
                {messages.map((msg, index) => (
                    <div key={index} className={`message-row ${msg.sender === 'user' ? 'user-row' : 'bot-row'}`}>
                        {msg.sender === 'bot' && <div className="avatar bot-avatar"><FaRobot /></div>}

                        <div className={`message-bubble ${msg.sender}`}>
                            {msg.text.split('\n').map((line, i) => <div key={i}>{line}</div>)}
                        </div>

                        {msg.sender === 'user' && <div className="avatar user-avatar"><FaUser /></div>}
                    </div>
                ))}
                {loading && (
                    <div className="message-row bot-row">
                        <div className="avatar bot-avatar"><FaRobot /></div>
                        <div className="message-bubble bot typing">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}

                {/* Suggestions Chips (Use translated suggestions) */}
                {!loading && messages[messages.length - 1]?.sender === 'bot' && (
                    <div className="suggestions-container">
                        {t.suggestions.map((s, i) => (
                            <button key={i} className="suggestion-chip" onClick={() => setInput(s)}>
                                {s}
                            </button>
                        ))}
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
                <input
                    type="text"
                    placeholder={t.placeholder}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <button type="submit" disabled={loading || !input.trim()}>
                    <FaPaperPlane />
                </button>
            </form>
        </div>
    );
};

export default Chatbot;
