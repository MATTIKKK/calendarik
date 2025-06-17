import React from 'react';
import { Calendar, Mail, Phone, MapPin, Twitter, Github, Linkedin } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main footer content */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand column */}
          <div className="md:col-span-1">
            <div className="flex items-center mb-6">
              <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-3 rounded-2xl mr-4">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold">Calendarik</span>
            </div>
            <p className="text-gray-400 leading-relaxed mb-6">
              The smart calendar with AI assistant that makes scheduling effortless and intelligent.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="bg-gray-800 p-3 rounded-xl hover:bg-gray-700 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="bg-gray-800 p-3 rounded-xl hover:bg-gray-700 transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="bg-gray-800 p-3 rounded-xl hover:bg-gray-700 transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product column */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Product</h3>
            <ul className="space-y-4 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Changelog</a></li>
            </ul>
          </div>

          {/* Company column */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Company</h3>
            <ul className="space-y-4 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Press</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Partners</a></li>
            </ul>
          </div>

          {/* Contact column */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Contact</h3>
            <ul className="space-y-4 text-gray-400">
              <li className="flex items-center">
                <Mail className="w-4 h-4 mr-3" />
                <a href="mailto:hello@calendarik.com" className="hover:text-white transition-colors">
                  hello@calendarik.com
                </a>
              </li>
              <li className="flex items-center">
                <Phone className="w-4 h-4 mr-3" />
                <a href="tel:+1-555-123-4567" className="hover:text-white transition-colors">
                  +1 (555) 123-4567
                </a>
              </li>
              <li className="flex items-start">
                <MapPin className="w-4 h-4 mr-3 mt-1 flex-shrink-0" />
                <span>
                  123 Innovation Street<br />
                  San Francisco, CA 94105
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom footer */}
        <div className="border-t border-gray-800 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2024 Calendarik. All rights reserved.
            </div>
            <div className="flex space-x-6 text-gray-400 text-sm">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;