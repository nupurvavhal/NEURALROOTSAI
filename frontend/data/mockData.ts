// Phase 2: Rich Data Structures

export interface Transaction {
  date: string;
  crop: string;
  amount: string;
  soldTo: string;
  revenue: number;
}

export interface Farmer {
  id: string;
  name: string;
  village: string;
  photoUrl: string;
  rating: number;
  totalEarnings: number;
  status: 'Connected' | 'Pending';
  history: Transaction[];
}

export interface Driver {
  id: string;
  name: string;
  vehicleType: string;
  lat: number;
  lng: number;
  status: 'Available' | 'Busy';
  currentLoad: string;
  phone: string;
}

export interface MarketItem {
  id: string;
  cropName: string;
  mandiName: string;
  price: number;
  trend: 'up' | 'down';
  spoilageRisk: 'Low' | 'Medium' | 'Critical';
}

export interface WholesalerPurchase {
  date: string;
  crop: string;
  quantity: string;
  boughtFrom: string;
  cost: number;
  soldTo?: string;
  revenue?: number;
  status: 'In Stock' | 'Sold' | 'In Transit';
}

export interface Wholesaler {
  id: string;
  name: string;
  businessName: string;
  location: string;
  photoUrl: string;
  rating: number;
  totalVolume: number;
  activeOrders: number;
  creditLimit: number;
  status: 'Active' | 'Inactive' | 'Pending Verification';
  specialization: string[];
  purchases: WholesalerPurchase[];
  phone: string;
  gstNumber: string;
}

// 10 Indian farmers with realistic transaction histories
export const farmersData: Farmer[] = [
  {
    id: 'F001',
    name: 'Ramesh Patil',
    village: 'Pune, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ramesh',
    rating: 4.8,
    totalEarnings: 245000,
    status: 'Connected',
    history: [
      { date: '2026-01-10', crop: 'Tomatoes', amount: '150kg', soldTo: 'Reliance Fresh', revenue: 22500 },
      { date: '2026-01-05', crop: 'Onions', amount: '200kg', soldTo: 'BigBasket', revenue: 18000 },
      { date: '2025-12-28', crop: 'Potatoes', amount: '300kg', soldTo: 'Local Mandi', revenue: 12000 },
      { date: '2025-12-20', crop: 'Cabbage', amount: '100kg', soldTo: 'DMart', revenue: 8500 },
    ],
  },
  {
    id: 'F002',
    name: 'Vikram Deshmukh',
    village: 'Nashik, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Vikram',
    rating: 4.9,
    totalEarnings: 320000,
    status: 'Connected',
    history: [
      { date: '2026-01-12', crop: 'Grapes', amount: '250kg', soldTo: 'BigBasket', revenue: 62500 },
      { date: '2026-01-08', crop: 'Onions', amount: '400kg', soldTo: 'Reliance Fresh', revenue: 36000 },
      { date: '2026-01-02', crop: 'Pomegranate', amount: '180kg', soldTo: 'Export House', revenue: 72000 },
      { date: '2025-12-25', crop: 'Grapes', amount: '300kg', soldTo: 'Local Trader', revenue: 75000 },
    ],
  },
  {
    id: 'F003',
    name: 'Suresh Kumar',
    village: 'Satara, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Suresh',
    rating: 4.5,
    totalEarnings: 180000,
    status: 'Connected',
    history: [
      { date: '2026-01-11', crop: 'Mangoes', amount: '120kg', soldTo: 'BigBasket', revenue: 24000 },
      { date: '2026-01-06', crop: 'Bananas', amount: '250kg', soldTo: 'Local Mandi', revenue: 15000 },
      { date: '2025-12-30', crop: 'Papayas', amount: '100kg', soldTo: 'DMart', revenue: 8000 },
    ],
  },
  {
    id: 'F004',
    name: 'Mahesh Jadhav',
    village: 'Kolhapur, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Mahesh',
    rating: 4.7,
    totalEarnings: 290000,
    status: 'Pending',
    history: [
      { date: '2026-01-09', crop: 'Sugarcane', amount: '500kg', soldTo: 'Sugar Mill', revenue: 15000 },
      { date: '2026-01-03', crop: 'Jaggery', amount: '200kg', soldTo: 'Local Trader', revenue: 40000 },
      { date: '2025-12-28', crop: 'Turmeric', amount: '150kg', soldTo: 'Spice Market', revenue: 45000 },
    ],
  },
  {
    id: 'F005',
    name: 'Vijay Singh Thakur',
    village: 'Ahmednagar, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Vijay',
    rating: 4.6,
    totalEarnings: 210000,
    status: 'Connected',
    history: [
      { date: '2026-01-13', crop: 'Wheat', amount: '400kg', soldTo: 'Grain Market', revenue: 16000 },
      { date: '2026-01-07', crop: 'Chickpeas', amount: '200kg', soldTo: 'BigBasket', revenue: 24000 },
      { date: '2025-12-29', crop: 'Sorghum', amount: '300kg', soldTo: 'Local Mandi', revenue: 12000 },
    ],
  },
  {
    id: 'F006',
    name: 'Rajendra Shinde',
    village: 'Solapur, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Rajendra',
    rating: 5.0,
    totalEarnings: 385000,
    status: 'Connected',
    history: [
      { date: '2026-01-12', crop: 'Cotton', amount: '300kg', soldTo: 'Textile Mill', revenue: 90000 },
      { date: '2026-01-05', crop: 'Groundnuts', amount: '250kg', soldTo: 'Oil Mill', revenue: 50000 },
      { date: '2025-12-27', crop: 'Sunflower', amount: '200kg', soldTo: 'Export House', revenue: 60000 },
    ],
  },
  {
    id: 'F007',
    name: 'Anil Yadav',
    village: 'Aurangabad, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Anil',
    rating: 4.4,
    totalEarnings: 165000,
    status: 'Connected',
    history: [
      { date: '2026-01-10', crop: 'Cauliflower', amount: '150kg', soldTo: 'Reliance Fresh', revenue: 15000 },
      { date: '2026-01-04', crop: 'Carrots', amount: '200kg', soldTo: 'Local Mandi', revenue: 12000 },
      { date: '2025-12-26', crop: 'Peas', amount: '100kg', soldTo: 'DMart', revenue: 10000 },
    ],
  },
  {
    id: 'F008',
    name: 'Prakash Desai',
    village: 'Sangli, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Prakash',
    rating: 4.8,
    totalEarnings: 275000,
    status: 'Pending',
    history: [
      { date: '2026-01-11', crop: 'Turmeric', amount: '180kg', soldTo: 'Spice Market', revenue: 54000 },
      { date: '2026-01-06', crop: 'Chili', amount: '120kg', soldTo: 'Export House', revenue: 36000 },
      { date: '2025-12-31', crop: 'Coriander', amount: '100kg', soldTo: 'Local Trader', revenue: 20000 },
    ],
  },
  {
    id: 'F009',
    name: 'Ashok Joshi',
    village: 'Jalgaon, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ashok',
    rating: 4.6,
    totalEarnings: 230000,
    status: 'Connected',
    history: [
      { date: '2026-01-13', crop: 'Bananas', amount: '350kg', soldTo: 'BigBasket', revenue: 21000 },
      { date: '2026-01-08', crop: 'Guavas', amount: '200kg', soldTo: 'Reliance Fresh', revenue: 16000 },
      { date: '2026-01-01', crop: 'Custard Apples', amount: '150kg', soldTo: 'Local Mandi', revenue: 22500 },
    ],
  },
  {
    id: 'F010',
    name: 'Ganesh Pawar',
    village: 'Ratnagiri, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Ganesh',
    rating: 4.9,
    totalEarnings: 340000,
    status: 'Connected',
    history: [
      { date: '2026-01-12', crop: 'Alphonso Mangoes', amount: '200kg', soldTo: 'Export House', revenue: 80000 },
      { date: '2026-01-07', crop: 'Cashews', amount: '100kg', soldTo: 'Processing Unit', revenue: 50000 },
      { date: '2026-01-02', crop: 'Kokum', amount: '150kg', soldTo: 'Local Trader', revenue: 30000 },
    ],
  },
];

// 8 drivers positioned around Mumbai/Pune coordinates
export const driversData: Driver[] = [
  {
    id: 'D001',
    name: 'Amit Deshmukh',
    vehicleType: 'Tata Ace',
    lat: 18.5204,
    lng: 73.8567,
    status: 'Available',
    currentLoad: 'Empty',
    phone: '+91 98765 43210',
  },
  {
    id: 'D002',
    name: 'Sunil Jadhav',
    vehicleType: 'Mahindra Pickup',
    lat: 19.0760,
    lng: 72.8777,
    status: 'Busy',
    currentLoad: '300kg Tomatoes',
    phone: '+91 98765 43211',
  },
  {
    id: 'D003',
    name: 'Rahul More',
    vehicleType: 'Tata 407',
    lat: 18.5642,
    lng: 73.9132,
    status: 'Available',
    currentLoad: 'Empty',
    phone: '+91 98765 43212',
  },
  {
    id: 'D004',
    name: 'Prakash Bhosale',
    vehicleType: 'Ashok Leyland Dost',
    lat: 19.2183,
    lng: 72.9781,
    status: 'Busy',
    currentLoad: '250kg Onions',
    phone: '+91 98765 43213',
  },
  {
    id: 'D005',
    name: 'Santosh Kulkarni',
    vehicleType: 'Tata Ace',
    lat: 18.4574,
    lng: 73.8544,
    status: 'Available',
    currentLoad: 'Empty',
    phone: '+91 98765 43214',
  },
  {
    id: 'D006',
    name: 'Mahesh Patil',
    vehicleType: 'Eicher Pro 1049',
    lat: 19.1136,
    lng: 72.8697,
    status: 'Busy',
    currentLoad: '500kg Potatoes',
    phone: '+91 98765 43215',
  },
  {
    id: 'D007',
    name: 'Ganesh Shinde',
    vehicleType: 'Mahindra Bolero Pickup',
    lat: 18.6298,
    lng: 73.7997,
    status: 'Available',
    currentLoad: 'Empty',
    phone: '+91 98765 43216',
  },
  {
    id: 'D008',
    name: 'Ravi Kamble',
    vehicleType: 'Tata 709',
    lat: 18.9894,
    lng: 72.8358,
    status: 'Available',
    currentLoad: 'Empty',
    phone: '+91 98765 43217',
  },
];

// 12 market items (fruits/vegetables)
export const marketItemsData: MarketItem[] = [
  {
    id: 'M001',
    cropName: 'Alphonso Mangoes',
    mandiName: 'Ratnagiri APMC',
    price: 400,
    trend: 'up',
    spoilageRisk: 'Critical',
  },
  {
    id: 'M002',
    cropName: 'Onions',
    mandiName: 'Nashik Mandi',
    price: 90,
    trend: 'down',
    spoilageRisk: 'Low',
  },
  {
    id: 'M003',
    cropName: 'Tomatoes',
    mandiName: 'Pune APMC',
    price: 150,
    trend: 'up',
    spoilageRisk: 'Critical',
  },
  {
    id: 'M004',
    cropName: 'Potatoes',
    mandiName: 'Kolhapur Market',
    price: 40,
    trend: 'down',
    spoilageRisk: 'Low',
  },
  {
    id: 'M005',
    cropName: 'Bananas',
    mandiName: 'Jalgaon APMC',
    price: 60,
    trend: 'up',
    spoilageRisk: 'Medium',
  },
  {
    id: 'M006',
    cropName: 'Grapes',
    mandiName: 'Nashik Grape Market',
    price: 250,
    trend: 'up',
    spoilageRisk: 'Critical',
  },
  {
    id: 'M007',
    cropName: 'Cauliflower',
    mandiName: 'Pune Vegetable Market',
    price: 100,
    trend: 'down',
    spoilageRisk: 'Medium',
  },
  {
    id: 'M008',
    cropName: 'Cabbage',
    mandiName: 'Satara Mandi',
    price: 85,
    trend: 'up',
    spoilageRisk: 'Low',
  },
  {
    id: 'M009',
    cropName: 'Pomegranate',
    mandiName: 'Solapur APMC',
    price: 400,
    trend: 'up',
    spoilageRisk: 'Medium',
  },
  {
    id: 'M010',
    cropName: 'Green Chili',
    mandiName: 'Sangli Spice Market',
    price: 300,
    trend: 'down',
    spoilageRisk: 'Critical',
  },
  {
    id: 'M011',
    cropName: 'Carrots',
    mandiName: 'Aurangabad Market',
    price: 60,
    trend: 'up',
    spoilageRisk: 'Low',
  },
  {
    id: 'M012',
    cropName: 'Spinach',
    mandiName: 'Mumbai Wholesale',
    price: 45,
    trend: 'down',
    spoilageRisk: 'Critical',
  },
];

// 12 wholesalers/traders with comprehensive business details
export const wholesalersData: Wholesaler[] = [
  {
    id: 'W001',
    name: 'Rajesh Mehta',
    businessName: 'Mehta Fresh Traders',
    location: 'Vashi APMC, Navi Mumbai',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=RajeshM',
    rating: 4.8,
    totalVolume: 850000,
    activeOrders: 12,
    creditLimit: 500000,
    status: 'Active',
    specialization: ['Vegetables', 'Fruits', 'Exotic Produce'],
    phone: '+91 98234 56789',
    gstNumber: '27AABCU9603R1ZP',
    purchases: [
      { date: '2026-01-14', crop: 'Tomatoes', quantity: '500kg', boughtFrom: 'Ramesh Patil', cost: 75000, soldTo: 'Reliance Fresh', revenue: 95000, status: 'Sold' },
      { date: '2026-01-13', crop: 'Onions', quantity: '800kg', boughtFrom: 'Vikram Deshmukh', cost: 72000, soldTo: 'BigBasket', revenue: 88000, status: 'Sold' },
      { date: '2026-01-12', crop: 'Cauliflower', quantity: '300kg', boughtFrom: 'Anil Yadav', cost: 30000, status: 'In Stock' },
      { date: '2026-01-11', crop: 'Grapes', quantity: '400kg', boughtFrom: 'Vikram Deshmukh', cost: 100000, soldTo: 'DMart', revenue: 125000, status: 'Sold' },
    ],
  },
  {
    id: 'W002',
    name: 'Sanjay Gupta',
    businessName: 'Gupta Agro Commodities',
    location: 'Pune APMC, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=SanjayG',
    rating: 4.9,
    totalVolume: 1250000,
    activeOrders: 18,
    creditLimit: 750000,
    status: 'Active',
    specialization: ['Grains', 'Pulses', 'Oilseeds'],
    phone: '+91 98765 12345',
    gstNumber: '27AABCU9604R1ZQ',
    purchases: [
      { date: '2026-01-15', crop: 'Wheat', quantity: '2000kg', boughtFrom: 'Vijay Singh', cost: 80000, soldTo: 'Grain Mills', revenue: 96000, status: 'Sold' },
      { date: '2026-01-13', crop: 'Chickpeas', quantity: '1000kg', boughtFrom: 'Vijay Singh', cost: 120000, status: 'In Transit' },
      { date: '2026-01-10', crop: 'Groundnuts', quantity: '500kg', boughtFrom: 'Rajendra Shinde', cost: 100000, soldTo: 'Oil Mill', revenue: 115000, status: 'Sold' },
    ],
  },
  {
    id: 'W003',
    name: 'Dinesh Patil',
    businessName: 'Maharashtra Fruit Merchants',
    location: 'Nashik Mandi, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=DineshP',
    rating: 4.7,
    totalVolume: 680000,
    activeOrders: 9,
    creditLimit: 400000,
    status: 'Active',
    specialization: ['Grapes', 'Pomegranate', 'Citrus Fruits'],
    phone: '+91 98876 54321',
    gstNumber: '27AABCU9605R1ZR',
    purchases: [
      { date: '2026-01-14', crop: 'Grapes', quantity: '600kg', boughtFrom: 'Vikram Deshmukh', cost: 150000, soldTo: 'Export House', revenue: 180000, status: 'Sold' },
      { date: '2026-01-12', crop: 'Pomegranate', quantity: '350kg', boughtFrom: 'Vikram Deshmukh', cost: 140000, status: 'In Stock' },
      { date: '2026-01-09', crop: 'Grapes', quantity: '500kg', boughtFrom: 'Vikram Deshmukh', cost: 125000, soldTo: 'BigBasket', revenue: 155000, status: 'Sold' },
    ],
  },
  {
    id: 'W004',
    name: 'Arun Kumar',
    businessName: 'Kumar Vegetable Hub',
    location: 'Mumbai Wholesale Market',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=ArunK',
    rating: 4.6,
    totalVolume: 920000,
    activeOrders: 15,
    creditLimit: 600000,
    status: 'Active',
    specialization: ['Leafy Vegetables', 'Root Vegetables', 'Exotic Veggies'],
    phone: '+91 98234 67890',
    gstNumber: '27AABCU9606R1ZS',
    purchases: [
      { date: '2026-01-15', crop: 'Spinach', quantity: '200kg', boughtFrom: 'Multiple Farmers', cost: 9000, soldTo: 'Local Retailers', revenue: 12000, status: 'Sold' },
      { date: '2026-01-14', crop: 'Carrots', quantity: '400kg', boughtFrom: 'Anil Yadav', cost: 24000, status: 'In Stock' },
      { date: '2026-01-13', crop: 'Potatoes', quantity: '1000kg', boughtFrom: 'Multiple Farmers', cost: 40000, soldTo: 'Hotels', revenue: 52000, status: 'Sold' },
    ],
  },
  {
    id: 'W005',
    name: 'Pradeep Shah',
    businessName: 'Shah Mango Exports',
    location: 'Ratnagiri, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=PradeepS',
    rating: 5.0,
    totalVolume: 1500000,
    activeOrders: 8,
    creditLimit: 1000000,
    status: 'Active',
    specialization: ['Alphonso Mangoes', 'Tropical Fruits', 'Export Quality'],
    phone: '+91 98765 43219',
    gstNumber: '27AABCU9607R1ZT',
    purchases: [
      { date: '2026-01-14', crop: 'Alphonso Mangoes', quantity: '800kg', boughtFrom: 'Ganesh Pawar', cost: 320000, soldTo: 'Dubai Export', revenue: 480000, status: 'In Transit' },
      { date: '2026-01-10', crop: 'Alphonso Mangoes', quantity: '600kg', boughtFrom: 'Ganesh Pawar', cost: 240000, soldTo: 'UK Export', revenue: 380000, status: 'Sold' },
      { date: '2026-01-07', crop: 'Cashews', quantity: '300kg', boughtFrom: 'Ganesh Pawar', cost: 150000, status: 'In Stock' },
    ],
  },
  {
    id: 'W006',
    name: 'Mohan Joshi',
    businessName: 'Joshi Spice Traders',
    location: 'Sangli Market, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=MohanJ',
    rating: 4.8,
    totalVolume: 720000,
    activeOrders: 11,
    creditLimit: 450000,
    status: 'Active',
    specialization: ['Turmeric', 'Chili', 'Spices'],
    phone: '+91 98876 12345',
    gstNumber: '27AABCU9608R1ZU',
    purchases: [
      { date: '2026-01-13', crop: 'Turmeric', quantity: '400kg', boughtFrom: 'Prakash Desai', cost: 120000, soldTo: 'Spice Mills', revenue: 145000, status: 'Sold' },
      { date: '2026-01-11', crop: 'Chili', quantity: '300kg', boughtFrom: 'Prakash Desai', cost: 90000, status: 'In Stock' },
      { date: '2026-01-08', crop: 'Coriander', quantity: '250kg', boughtFrom: 'Prakash Desai', cost: 50000, soldTo: 'Local Market', revenue: 62500, status: 'Sold' },
    ],
  },
  {
    id: 'W007',
    name: 'Suresh Reddy',
    businessName: 'Reddy Cotton & Grains',
    location: 'Solapur APMC, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=SureshR',
    rating: 4.5,
    totalVolume: 980000,
    activeOrders: 14,
    creditLimit: 550000,
    status: 'Active',
    specialization: ['Cotton', 'Sorghum', 'Millets'],
    phone: '+91 98234 11111',
    gstNumber: '27AABCU9609R1ZV',
    purchases: [
      { date: '2026-01-15', crop: 'Cotton', quantity: '600kg', boughtFrom: 'Rajendra Shinde', cost: 180000, soldTo: 'Textile Mills', revenue: 210000, status: 'Sold' },
      { date: '2026-01-12', crop: 'Sorghum', quantity: '500kg', boughtFrom: 'Vijay Singh', cost: 20000, status: 'In Stock' },
      { date: '2026-01-09', crop: 'Sunflower', quantity: '400kg', boughtFrom: 'Rajendra Shinde', cost: 120000, soldTo: 'Oil Mill', revenue: 145000, status: 'Sold' },
    ],
  },
  {
    id: 'W008',
    name: 'Kiran Deshmukh',
    businessName: 'Deshmukh Banana Traders',
    location: 'Jalgaon, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=KiranD',
    rating: 4.7,
    totalVolume: 560000,
    activeOrders: 10,
    creditLimit: 350000,
    status: 'Active',
    specialization: ['Bananas', 'Tropical Fruits', 'Local Distribution'],
    phone: '+91 98765 22222',
    gstNumber: '27AABCU9610R1ZW',
    purchases: [
      { date: '2026-01-14', crop: 'Bananas', quantity: '700kg', boughtFrom: 'Ashok Joshi', cost: 42000, soldTo: 'Retail Chains', revenue: 55000, status: 'Sold' },
      { date: '2026-01-12', crop: 'Guavas', quantity: '300kg', boughtFrom: 'Ashok Joshi', cost: 24000, status: 'In Stock' },
      { date: '2026-01-10', crop: 'Bananas', quantity: '600kg', boughtFrom: 'Ashok Joshi', cost: 36000, soldTo: 'Hotels', revenue: 48000, status: 'Sold' },
    ],
  },
  {
    id: 'W009',
    name: 'Vijay Kulkarni',
    businessName: 'Kulkarni Organic Traders',
    location: 'Satara Mandi, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=VijayK',
    rating: 4.9,
    totalVolume: 420000,
    activeOrders: 7,
    creditLimit: 300000,
    status: 'Active',
    specialization: ['Organic Produce', 'Premium Quality', 'Health Foods'],
    phone: '+91 98876 33333',
    gstNumber: '27AABCU9611R1ZX',
    purchases: [
      { date: '2026-01-13', crop: 'Organic Mangoes', quantity: '250kg', boughtFrom: 'Suresh Kumar', cost: 50000, soldTo: 'Organic Stores', revenue: 67500, status: 'Sold' },
      { date: '2026-01-11', crop: 'Papayas', quantity: '200kg', boughtFrom: 'Suresh Kumar', cost: 16000, status: 'In Stock' },
      { date: '2026-01-08', crop: 'Bananas', quantity: '300kg', boughtFrom: 'Suresh Kumar', cost: 18000, soldTo: 'Health Centers', revenue: 25000, status: 'Sold' },
    ],
  },
  {
    id: 'W010',
    name: 'Ramesh Sawant',
    businessName: 'Sawant Sugar & Jaggery',
    location: 'Kolhapur, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=RameshS',
    rating: 4.6,
    totalVolume: 1100000,
    activeOrders: 16,
    creditLimit: 700000,
    status: 'Active',
    specialization: ['Sugarcane', 'Jaggery', 'Sugar Products'],
    phone: '+91 98234 44444',
    gstNumber: '27AABCU9612R1ZY',
    purchases: [
      { date: '2026-01-14', crop: 'Sugarcane', quantity: '2000kg', boughtFrom: 'Mahesh Jadhav', cost: 60000, soldTo: 'Sugar Mill', revenue: 75000, status: 'Sold' },
      { date: '2026-01-12', crop: 'Jaggery', quantity: '500kg', boughtFrom: 'Mahesh Jadhav', cost: 100000, status: 'In Transit' },
      { date: '2026-01-09', crop: 'Turmeric', quantity: '300kg', boughtFrom: 'Mahesh Jadhav', cost: 90000, soldTo: 'Processing Unit', revenue: 110000, status: 'Sold' },
    ],
  },
  {
    id: 'W011',
    name: 'Ashok Bhosale',
    businessName: 'Bhosale Fresh Produce',
    location: 'Aurangabad Market, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=AshokB',
    rating: 4.4,
    totalVolume: 380000,
    activeOrders: 6,
    creditLimit: 250000,
    status: 'Pending Verification',
    specialization: ['Mixed Vegetables', 'Local Market', 'Bulk Supply'],
    phone: '+91 98765 55555',
    gstNumber: '27AABCU9613R1ZZ',
    purchases: [
      { date: '2026-01-13', crop: 'Cauliflower', quantity: '300kg', boughtFrom: 'Anil Yadav', cost: 30000, status: 'In Stock' },
      { date: '2026-01-11', crop: 'Carrots', quantity: '400kg', boughtFrom: 'Anil Yadav', cost: 24000, soldTo: 'Local Retailers', revenue: 32000, status: 'Sold' },
      { date: '2026-01-08', crop: 'Peas', quantity: '200kg', boughtFrom: 'Anil Yadav', cost: 20000, status: 'In Stock' },
    ],
  },
  {
    id: 'W012',
    name: 'Prakash Jadhav',
    businessName: 'Jadhav Multi-Commodity Exchange',
    location: 'Ahmednagar APMC, Maharashtra',
    photoUrl: 'https://api.dicebear.com/7.x/bottts-neutral/svg?seed=PrakashJ',
    rating: 4.8,
    totalVolume: 1350000,
    activeOrders: 20,
    creditLimit: 900000,
    status: 'Active',
    specialization: ['All Commodities', 'Bulk Trading', 'B2B Supply'],
    phone: '+91 98876 66666',
    gstNumber: '27AABCU9614R1AA',
    purchases: [
      { date: '2026-01-15', crop: 'Wheat', quantity: '1500kg', boughtFrom: 'Vijay Singh', cost: 60000, soldTo: 'Food Processing', revenue: 75000, status: 'Sold' },
      { date: '2026-01-14', crop: 'Chickpeas', quantity: '800kg', boughtFrom: 'Vijay Singh', cost: 96000, status: 'In Transit' },
      { date: '2026-01-13', crop: 'Sorghum', quantity: '600kg', boughtFrom: 'Vijay Singh', cost: 24000, soldTo: 'Grain Mills', revenue: 31000, status: 'Sold' },
      { date: '2026-01-10', crop: 'Mixed Produce', quantity: '2000kg', boughtFrom: 'Multiple Farmers', cost: 150000, status: 'In Stock' },
    ],
  },
];
