import SentimentByIssue from '../components/SentimentByIssue'
import SentimentTrends from '../components/SentimentTrends'
import SentimentDistribution from '../components/SentimentDistribution'
import IssueImportance from '../components/IssueImportance'
import CompetitorComparison from '../components/CompetitorComparison'
import SentimentHeatmap from '../components/SentimentHeatmap'
import InfluencerTracking from '../components/InfluencerTracking'
import AlertsPanel from '../components/AlertsPanel'
import { MapboxTamilNadu } from '../components/maps/MapboxTamilNadu'
import ExportManager from '../components/ExportManager'
import AdvancedChart from '../components/AdvancedChart'
import { MobileNavigation, ResponsiveContainer, MobileCard, ResponsiveGrid, MobileButton, MobileStats } from '../components/MobileResponsive'
import { TrendingUp, Users, AlertTriangle, Target, Calendar, Brain, Zap, Globe, Lightbulb } from 'lucide-react'
import { useState, useEffect } from 'react'
import { realTimeService } from '../services/realTimeService'
import { crisisDetection } from '../services/crisisDetection'
import { recommendationsEngine } from '../services/recommendationsEngine'


export default function Dashboard() {
  const [liveMetrics, setLiveMetrics] = useState<any>(null);
  const [activeAlerts, setActiveAlerts] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<any[]>([]);
  const [recentPosts, setRecentPosts] = useState<any[]>([]);
  const [showAdvancedFeatures, setShowAdvancedFeatures] = useState(false);

  // Initialize real-time services
  useEffect(() => {
    const initServices = async () => {
      try {
        await realTimeService.connect();
        crisisDetection.startMonitoring();
        
        // Update context for recommendations - Tamil Nadu & Puducherry specific
        const context = {
          current_sentiment: {
            overall: 0.67,
            by_issue: {
              'water': 0.42, // Critical issue in TN
              'jobs': 0.48,
              'agriculture': 0.51,
              'education': 0.65,
              'caste_reservation': 0.58,
              'health': 0.70,
              'prohibition': 0.55,
              'tamil_language': 0.73
            },
            by_location: {
              'Chennai': 0.68,
              'Coimbatore': 0.71,
              'Madurai': 0.62,
              'Tiruchirappalli': 0.58,
              'Salem': 0.65,
              'Tirunelveli': 0.56,
              'Tiruppur': 0.69,
              'Puducherry': 0.64
            },
            trend_direction: 'improving' as const
          },
          trending_topics: realTimeService.getTrendingTopics(),
          recent_posts: realTimeService.getSocialMediaPosts(50),
          active_crises: crisisDetection.getActiveEvents(),
          field_reports: [],
          competitor_activity: {
            sentiment: 0.45,
            volume: 250,
            key_messages: [
              'DMK: Social welfare schemes',
              'AIADMK: MGR-Amma legacy',
              'BJP: Development & nationalism',
              'PMK: Vanniyar reservation',
              'NTK: Tamil nationalism'
            ]
          },
          campaign_calendar: {
            upcoming_events: [
              {
                date: new Date(Date.now() + 86400000 * 3),
                type: 'rally' as const,
                location: 'Chennai',
                expected_attendance: 50000
              },
              {
                date: new Date(Date.now() + 86400000 * 7),
                type: 'rally' as const,
                location: 'Coimbatore',
                expected_attendance: 30000
              }
            ],
            recent_activities: []
          },
          resource_availability: {
            budget: 10000000,
            volunteers: 5000,
            time_to_election: 180, // Assuming 6 months to election
            key_demographics: [
              'Youth (18-35)',
              'First-time voters',
              'OBC/MBC communities',
              'Urban middle class',
              'Farmers',
              'Women voters'
            ]
          }
        };
        
        recommendationsEngine.updateContext(context);
        await recommendationsEngine.generateRecommendations();
        
        console.log('Dashboard services initialized successfully');
      } catch (error) {
        console.error('Failed to initialize dashboard services:', error);
      }
    };
    
    initServices();
    
    // Set up real-time subscriptions
    const unsubscribeMetrics = realTimeService.subscribe('metrics-live', (data: any) => {
      setLiveMetrics(data.data);
    });
    
    const unsubscribeAlerts = realTimeService.subscribe('alerts-live', (data: any) => {
      if (data.data) {
        setActiveAlerts(prev => [data.data, ...prev.slice(0, 9)]);
      }
    });
    
    const unsubscribeCrisis = crisisDetection.subscribe((event) => {
      setActiveAlerts(prev => [{
        id: event.id,
        title: event.title,
        description: event.description,
        severity: event.severity,
        timestamp: event.detected_at,
        type: 'crisis'
      }, ...prev.slice(0, 9)]);
    });
    
    const unsubscribeRecommendations = recommendationsEngine.subscribe((recs) => {
      setRecommendations(recs.slice(0, 5));
    });
    
    // Update data periodically
    const interval = setInterval(() => {
      setTrendingTopics(realTimeService.getTrendingTopics().slice(0, 8));
      setRecentPosts(realTimeService.getSocialMediaPosts(10));
    }, 30000);
    
    return () => {
      unsubscribeMetrics();
      unsubscribeAlerts();
      unsubscribeCrisis();
      unsubscribeRecommendations();
      clearInterval(interval);
      realTimeService.disconnect();
      crisisDetection.stopMonitoring();
    };
  }, []);

  const kpis = [
    { label: 'TVK Overall Sentiment', value: liveMetrics?.overallSentiment ? `${liveMetrics.overallSentiment}%` : '67%', change: '+5%', icon: TrendingUp, color: 'text-green-600' },
    { label: 'Active Conversations (Tamil)', value: liveMetrics?.activeConversations?.toLocaleString() || '25.3K', change: '+18%', icon: Users, color: 'text-blue-600' },
    { label: 'Critical Alerts', value: activeAlerts.filter(a => a.severity === 'critical').length.toString() || '3', change: '-2', icon: AlertTriangle, color: 'text-red-600' },
    { label: 'Top Issue (TN)', value: trendingTopics[0]?.keyword || 'Water', change: '32%', icon: Target, color: 'text-purple-600' },
    { label: 'Constituencies Covered', value: '264', change: 'TN+PY', icon: Globe, color: 'text-orange-600' }
  ]

  // Tamil Nadu Districts Map Data (38 districts)
  const tamilNaduMapData = [
    { id: 'TN-Chennai', title: 'Chennai', value: 68, sentiment: 0.68, constituencies: 16 },
    { id: 'TN-Coimbatore', title: 'Coimbatore', value: 71, sentiment: 0.71, constituencies: 10 },
    { id: 'TN-Madurai', title: 'Madurai', value: 62, sentiment: 0.62, constituencies: 6 },
    { id: 'TN-Tiruchirappalli', title: 'Tiruchirappalli', value: 58, sentiment: 0.58, constituencies: 6 },
    { id: 'TN-Salem', title: 'Salem', value: 65, sentiment: 0.65, constituencies: 7 },
    { id: 'TN-Tirunelveli', title: 'Tirunelveli', value: 56, sentiment: 0.56, constituencies: 6 },
    { id: 'TN-Tiruppur', title: 'Tiruppur', value: 69, sentiment: 0.69, constituencies: 6 },
    { id: 'TN-Erode', title: 'Erode', value: 63, sentiment: 0.63, constituencies: 6 },
    { id: 'TN-Vellore', title: 'Vellore', value: 64, sentiment: 0.64, constituencies: 5 },
    { id: 'TN-Thanjavur', title: 'Thanjavur', value: 60, sentiment: 0.60, constituencies: 5 },
    { id: 'TN-Kanchipuram', title: 'Kanchipuram', value: 67, sentiment: 0.67, constituencies: 7 },
    { id: 'TN-Cuddalore', title: 'Cuddalore', value: 61, sentiment: 0.61, constituencies: 4 },
    { id: 'TN-Dindigul', title: 'Dindigul', value: 59, sentiment: 0.59, constituencies: 5 },
    { id: 'TN-Karur', title: 'Karur', value: 66, sentiment: 0.66, constituencies: 3 },
    { id: 'TN-Namakkal', title: 'Namakkal', value: 68, sentiment: 0.68, constituencies: 4 },
    { id: 'TN-Puducherry', title: 'Puducherry', value: 64, sentiment: 0.64, constituencies: 30 }
  ]

  return (
    <>
      <MobileNavigation />
      <ResponsiveContainer>
        <div className="space-responsive pt-16 lg:pt-0">
          <div className="mobile-header lg:mb-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              <div>
                <h1 className="text-responsive-xl font-bold text-gray-900">Pulse of People Dashboard</h1>
                <p className="text-responsive-sm text-gray-600">Real-time political intelligence and sentiment analysis</p>
              </div>
              <div className="flex space-x-2 lg:space-x-3">
                <ExportManager className="inline-block" />
                <MobileButton
                  onClick={() => setShowAdvancedFeatures(!showAdvancedFeatures)}
                  variant={showAdvancedFeatures ? 'primary' : 'outline'}
                  size="default"
                >
                  <Brain className="w-4 h-4 inline mr-2" />
                  AI Features
                </MobileButton>
              </div>
            </div>
          </div>

          <MobileStats stats={kpis.map((kpi, index) => {
            const liveValue = liveMetrics && index === 0 ? `${liveMetrics.overallSentiment}%` :
                            liveMetrics && index === 1 ? liveMetrics.activeConversations?.toLocaleString() :
                            liveMetrics && index === 2 ? liveMetrics.criticalAlerts?.toString() :
                            kpi.value;
            
            return {
              label: kpi.label,
              value: liveValue,
              icon: kpi.icon,
              color: kpi.color.includes('green') ? 'bg-green-100' :
                     kpi.color.includes('blue') ? 'bg-blue-100' :
                     kpi.color.includes('red') ? 'bg-red-100' :
                     kpi.color.includes('purple') ? 'bg-purple-100' :
                     'bg-gray-100',
              trend: { direction: kpi.change.includes('+') ? 'up' : 'down', value: kpi.change }
            };
          })} />

          {/* AI-Powered Features Section */}
          {showAdvancedFeatures && (
            <MobileCard className="border-2 border-purple-200 bg-purple-50" padding="default">
              <div className="space-responsive">
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-bold text-purple-900">AI-Powered Intelligence</h2>
          </div>
          
                <ResponsiveGrid cols={{ sm: 1, lg: 2, xl: 3 }}>
                  {/* Crisis Alerts */}
                  {activeAlerts.length > 0 && (
                    <MobileCard className="border-red-200" padding="default">
                      <div className="flex items-center space-x-2 mb-3">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <h3 className="text-responsive-sm font-semibold text-red-900">Crisis Detection</h3>
                      </div>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {activeAlerts.slice(0, 3).map((alert, index) => (
                          <div key={index} className={`p-2 rounded text-responsive-xs ${
                            alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                            alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            <div className="font-medium">{alert.title}</div>
                            <div className="text-xs opacity-75">{alert.description}</div>
                          </div>
                        ))}
                      </div>
                    </MobileCard>
                  )}
            
                  {/* AI Recommendations */}
                  {recommendations.length > 0 && (
                    <MobileCard className="border-blue-200" padding="default">
                      <div className="flex items-center space-x-2 mb-3">
                        <Lightbulb className="w-5 h-5 text-blue-600" />
                        <h3 className="text-responsive-sm font-semibold text-blue-900">AI Recommendations</h3>
                      </div>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {recommendations.slice(0, 3).map((rec, index) => (
                          <div key={index} className={`p-2 rounded text-responsive-xs ${
                            rec.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                            rec.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            <div className="font-medium">{rec.title}</div>
                            <div className="text-xs opacity-75">{rec.description}</div>
                            <div className="text-xs mt-1 font-medium">Impact: {rec.estimated_impact} | Confidence: {Math.round(rec.confidence_score * 100)}%</div>
                          </div>
                        ))}
                      </div>
                    </MobileCard>
                  )}
            
                  {/* Trending Topics */}
                  {trendingTopics.length > 0 && (
                    <MobileCard className="border-green-200" padding="default">
                      <div className="flex items-center space-x-2 mb-3">
                        <Zap className="w-5 h-5 text-green-600" />
                        <h3 className="text-responsive-sm font-semibold text-green-900">Trending Topics</h3>
                      </div>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {trendingTopics.slice(0, 5).map((topic, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-green-50 rounded text-responsive-xs">
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-green-800 truncate">{topic.keyword}</div>
                              <div className="text-green-600 truncate">Volume: {topic.volume} | Growth: +{Math.round(topic.growth_rate * 100)}%</div>
                            </div>
                            <div className={`px-2 py-1 rounded text-xs flex-shrink-0 ${
                              topic.sentiment_score > 0.1 ? 'bg-green-200 text-green-800' :
                              topic.sentiment_score < -0.1 ? 'bg-red-200 text-red-800' :
                              'bg-gray-200 text-gray-800'
                            }`}>
                              {topic.sentiment_score > 0.1 ? '😊' : topic.sentiment_score < -0.1 ? '😟' : '😐'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </MobileCard>
                  )}
                </ResponsiveGrid>
          
                {/* Advanced Visualizations */}
                <ResponsiveGrid cols={{ sm: 1, lg: 2 }}>
                  {liveMetrics?.trendingTopics && (
                    <AdvancedChart
                      type="doughnut"
                      title="Platform Distribution"
                      subtitle="Posts by social media platform"
                      data={{
                        labels: ['Twitter', 'Facebook', 'Instagram', 'YouTube', 'News'],
                        datasets: [{
                          label: 'Posts',
                          data: [
                            liveMetrics.engagement?.twitter || 0,
                            liveMetrics.engagement?.facebook || 0,
                            liveMetrics.engagement?.instagram || 0,
                            liveMetrics.engagement?.youtube || 0,
                            liveMetrics.engagement?.news || 0
                          ],
                          backgroundColor: [
                            '#1DA1F2',
                            '#4267B2', 
                            '#E4405F',
                            '#FF0000',
                            '#6B7280'
                          ]
                        }]
                      }}
                      height={250}
                      showExport={true}
                    />
                  )}
                  
                  {recentPosts.length > 0 && (
                    <MobileCard padding="default">
                      <div className="flex items-center space-x-2 mb-3">
                        <Globe className="w-5 h-5 text-gray-600" />
                        <h3 className="text-responsive-sm font-semibold text-gray-900">Recent Social Media Activity</h3>
                      </div>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {recentPosts.slice(0, 5).map((post, index) => (
                          <div key={index} className="p-2 bg-gray-50 rounded text-responsive-xs">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-gray-800 truncate flex-1">{post.source?.platform || 'Social Media'}</span>
                              <span className={`px-1 py-0.5 rounded text-xs flex-shrink-0 ${
                                post.sentiment?.polarity === 'positive' ? 'bg-green-200 text-green-800' :
                                post.sentiment?.polarity === 'negative' ? 'bg-red-200 text-red-800' :
                                'bg-gray-200 text-gray-800'
                              }`}>
                                {post.sentiment?.polarity || 'neutral'}
                              </span>
                            </div>
                            <div className="text-gray-600 truncate">
                              {post.content?.substring(0, 100) || 'Sample social media content'}...
                            </div>
                            <div className="text-gray-500 mt-1 text-xs">
                              {post.engagement_metrics ? 
                                `👍 ${post.engagement_metrics.likes} 🔄 ${post.engagement_metrics.shares} 💬 ${post.engagement_metrics.comments}` :
                                'Engagement metrics'
                              }
                            </div>
                          </div>
                        ))}
                      </div>
                    </MobileCard>
                  )}
                </ResponsiveGrid>
              </div>
            </MobileCard>
          )}

          <div className="w-full">
            <MapboxTamilNadu height="600px" onConstituencyClick={(constituency) => console.log('Clicked:', constituency)} />
          </div>

          <ResponsiveGrid cols={{ sm: 1, lg: 2, xl: 3 }}>
            <SentimentByIssue />
            <SentimentTrends />
            <SentimentDistribution />
            <IssueImportance />
            <CompetitorComparison />
            <SentimentHeatmap />
          </ResponsiveGrid>

          <ResponsiveGrid cols={{ sm: 1, lg: 2 }}>
            <InfluencerTracking />
            <AlertsPanel />
          </ResponsiveGrid>
      
          {/* Enhanced Analytics Section */}
          {showAdvancedFeatures && liveMetrics && (
            <ResponsiveGrid cols={{ sm: 1, lg: 2 }}>
          <AdvancedChart
            type="line"
            title="Real-time Sentiment Trends"
            subtitle="Multi-language sentiment analysis over time"
            data={{
              labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
              datasets: [{
                label: 'Overall Sentiment',
                data: [0.65, 0.62, 0.68, 0.70, 0.67, 0.69, liveMetrics.overallSentiment / 100],
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
              }]
            }}
            height={300}
            showExport={true}
            showFilters={true}
            showZoom={true}
          />
          
          <AdvancedChart
            type="bar"
            title="Issue Sentiment Distribution"
            subtitle="Sentiment analysis by key political issues"
            data={{
              labels: ['Jobs', 'Healthcare', 'Education', 'Infrastructure', 'Law & Order'],
              datasets: [{
                label: 'Positive Sentiment',
                data: [45, 72, 60, 55, 48],
                backgroundColor: '#10B981'
              }, {
                label: 'Negative Sentiment', 
                data: [35, 18, 25, 30, 42],
                backgroundColor: '#EF4444'
              }, {
                label: 'Neutral Sentiment',
                data: [20, 10, 15, 15, 10],
                backgroundColor: '#6B7280'
              }]
            }}
            height={300}
            showExport={true}
          />
            </ResponsiveGrid>
          )}
        </div>
      </ResponsiveContainer>
    </>
  )
}