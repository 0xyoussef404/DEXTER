'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Brain, Target, Database, Activity, Sun, Moon } from 'lucide-react';

export default function Page() {
  const [scheme, setScheme] = useState('light');

  useEffect(() => {
    const stored = localStorage.getItem('color-scheme');
    const prefers = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = stored || (prefers ? 'dark' : 'light');
    setScheme(initial);
    document.documentElement.className = `${initial}-scheme`;
  }, []);

  const toggleScheme = () => {
    const next = scheme === 'light' ? 'dark' : 'light';
    setScheme(next);
    localStorage.setItem('color-scheme', next);
    document.documentElement.className = `${next}-scheme`;
  };

  const features = [
    { Icon: Shield, name: 'Reconnaissance', info: 'Multi-source intelligence gathering with 15+ data providers' },
    { Icon: Zap, name: 'XSS Scanner', info: 'Context-aware detection with bypass capabilities' },
    { Icon: Brain, name: 'ML Validation', info: 'Six-layer verification achieving 97% accuracy' },
    { Icon: Database, name: 'SQLi Testing', info: 'Statistical analysis across multiple techniques' },
    { Icon: Target, name: 'Fuzzing', info: 'Mutation-based testing with anomaly detection' },
    { Icon: Activity, name: 'Monitoring', info: 'Real-time updates via WebSocket connection' },
  ];

  return (
    <div style={{ background: `rgb(var(--bg-main))`, color: `rgb(var(--tx-main))`, minHeight: '100vh' }}>
      <nav style={{ position: 'sticky', top: 0, zIndex: 50, backdropFilter: 'blur(12px)', background: `rgb(var(--bg-card) / 0.7)`, borderBottom: `1px solid rgb(var(--bd-line))` }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Shield size={32} style={{ color: `rgb(var(--ac-blue))` }} />
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>BugHunterX</h1>
          </div>
          <button
            onClick={toggleScheme}
            style={{ padding: '0.75rem', borderRadius: '0.75rem', background: `rgb(var(--bg-main))`, border: `1px solid rgb(var(--bd-line))`, cursor: 'pointer', transition: 'transform 0.2s' }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            {scheme === 'light' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </nav>

      <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '5rem 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '5rem' }} className="anim-slide-up">
          <h2 style={{ fontSize: '4rem', fontWeight: 900, marginBottom: '1.5rem', lineHeight: 1.1 }}>
            Enterprise Security
            <br />
            <span style={{ background: `linear-gradient(to right, rgb(var(--ac-blue)), rgb(var(--ac-purple)))`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              Testing Platform
            </span>
          </h2>
          <p style={{ fontSize: '1.25rem', color: `rgb(var(--tx-soft))`, maxWidth: '48rem', margin: '0 auto 2.5rem' }}>
            Professional web application security assessment with AI-powered analysis and comprehensive vulnerability detection
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{ padding: '1rem 2rem', background: `rgb(var(--ac-blue))`, color: 'white', borderRadius: '0.75rem', fontWeight: 600, border: 'none', cursor: 'pointer', fontSize: '1rem' }}
            >
              Start Scan
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{ padding: '1rem 2rem', background: `rgb(var(--bg-card))`, color: `rgb(var(--tx-main))`, borderRadius: '0.75rem', fontWeight: 600, border: `1px solid rgb(var(--bd-line))`, cursor: 'pointer', fontSize: '1rem' }}
            >
              Learn More
            </motion.button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '5rem' }} className="anim-fade-in">
          {[
            { label: 'Vulnerabilities Found', val: '28,540+', Icon: Target },
            { label: 'Detection Rate', val: '97.8%', Icon: Brain },
            { label: 'Active Scans', val: '1,432', Icon: Activity },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              whileHover={{ y: -8, scale: 1.02 }}
              style={{ background: `rgb(var(--bg-card))`, padding: '2rem', borderRadius: '1.5rem', border: `1px solid rgb(var(--bd-line))`, boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
            >
              <stat.Icon size={40} style={{ color: `rgb(var(--ac-blue))`, marginBottom: '1rem' }} />
              <div style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '0.5rem' }}>{stat.val}</div>
              <div style={{ color: `rgb(var(--tx-soft))`, fontSize: '1rem' }}>{stat.label}</div>
            </motion.div>
          ))}
        </div>

        <h3 style={{ fontSize: '2.5rem', fontWeight: 900, textAlign: 'center', marginBottom: '3rem' }}>Core Capabilities</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -10, scale: 1.02 }}
              style={{ background: `rgb(var(--bg-card))`, padding: '2rem', borderRadius: '1.5rem', border: `1px solid rgb(var(--bd-line))`, boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
            >
              <div style={{ width: '3.5rem', height: '3.5rem', borderRadius: '1rem', background: `linear-gradient(to bottom right, rgb(var(--ac-blue)), rgb(var(--ac-purple)))`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                <f.Icon size={28} color="white" />
              </div>
              <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.75rem' }}>{f.name}</h4>
              <p style={{ color: `rgb(var(--tx-soft))`, lineHeight: 1.6 }}>{f.info}</p>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
