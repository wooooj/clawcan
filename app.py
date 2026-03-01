from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import json
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

class JDParseEngine:
    def __init__(self):
        # 技术栈识别模式
        self.tech_patterns = {
            'python': r'\b(python|django|flask|fastapi)\b',
            'javascript': r'\b(javascript|js|react|vue|angular|node\.?js|typescript)\b',
            'java': r'\b(java|spring|hibernate|j2ee)\b',
            'go': r'\b(golang|go\s+language|go\s+programming)\b',
            'rust': r'\b(rust|rustlang)\b',
            'c_sharp': r'\b(c#|c\s*sharp|\.net|asp\.net)\b',
            'c_plus_plus': r'\b(c\+\+|cpp|cplusplus)\b',
            'sql': r'\b(sql|mysql|postgresql|oracle|mssql)\b',
            'nosql': r'\b(mongodb|redis|elasticsearch|cassandra)\b',
            'cloud': r'\b(aws|azure|gcp|阿里云|腾讯云|华为云)\b',
            'devops': r'\b(docker|kubernetes|jenkins|gitlab|ci/cd)\b',
            'ml_ai': r'\b(machine learning|deep learning|tensorflow|pytorch|ai|nlp)\b'
        }
        
        # 学历层级
        self.degree_levels = ['博士', '硕士', '本科', '大专', '高中']
        self.degree_patterns = {
            '博士': r'\b(博士|phd|doctor)\b',
            '硕士': r'\b(硕士|master|m\.sc)\b', 
            '本科': r'\b(本科|学士|bachelor|bs|ba)\b',
            '大专': r'\b(大专|专科|associate)\b'
        }
        
        # 经验年限模式
        self.experience_patterns = [
            r'(\d+)\s*年.*经验',
            r'(\d+)\s*年.*开发',
            r'(\d+)\s*年.*工作',
            r'经验\s*(\d+)\s*年',
            r'至少\s*(\d+)\s*年'
        ]
        
        # 软技能关键词
        self.soft_skills = {
            'communication': ['沟通', '表达', '协调', '团队合作'],
            'leadership': ['领导', '管理', '带领', '项目管理'],
            'problem_solving': ['解决问题', '分析', 'debug', '优化'],
            'learning': ['学习', '快速上手', '自驱', '主动']
        }
        
        # 行业背景关键词
        self.industries = {
            '互联网': ['互联网', 'web', 'app', 'saas', '电商'],
            '金融科技': ['金融', '银行', '支付', '保险', 'fintech'],
            '游戏': ['游戏', 'game', 'unity', 'unreal'],
            '人工智能': ['ai', '人工智能', '机器学习', '深度学习'],
            '物联网': ['iot', '物联网', '嵌入式', '硬件'],
            '医疗健康': ['医疗', 'healthcare', '生物', '医药']
        }

    def extract_hard_requirements(self, jd_text: str) -> Dict[str, Any]:
        """提取硬性指标"""
        jd_lower = jd_text.lower()
        
        # 技术栈识别
        tech_stack = []
        for tech, pattern in self.tech_patterns.items():
            if re.search(pattern, jd_lower, re.IGNORECASE):
                tech_stack.append(tech.replace('_', ' ').title())
        
        # 工作年限
        years_exp = 0
        for pattern in self.experience_patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                years_exp = max(years_exp, int(match.group(1)))
                break
        
        # 学历要求
        education = "不限"
        for level, pattern in self.degree_patterns.items():
            if re.search(pattern, jd_text, re.IGNORECASE):
                education = level
                break
        
        return {
            "tech_stack": list(set(tech_stack)),
            "years_experience": years_exp,
            "education": education
        }
    
    def extract_soft_requirements(self, jd_text: str) -> Dict[str, Any]:
        """提取软性指标"""
        jd_lower = jd_text.lower()
        
        # 行业背景
        industry_background = []
        for industry, keywords in self.industries.items():
            if any(keyword in jd_lower for keyword in keywords):
                industry_background.append(industry)
        
        # 跳槽频率容忍度（基于稳定性关键词）
        stability_keywords = ['稳定', '长期', '忠诚', '不跳槽', '踏实']
        job_hopping_tolerance = "高"  # 默认高容忍
        if any(keyword in jd_lower for keyword in stability_keywords):
            job_hopping_tolerance = "低"
        
        # 大厂经历偏好
        big_tech_keywords = ['大厂', '一线', '知名', '头部', 'top', 'fortune']
        big_tech_preference = any(keyword in jd_lower for keyword in big_tech_keywords)
        
        # 软技能要求
        required_soft_skills = []
        for skill_category, keywords in self.soft_skills.items():
            if any(keyword in jd_lower for keyword in keywords):
                required_soft_skills.append(skill_category.replace('_', ' ').title())
        
        return {
            "industry_background": industry_background if industry_background else ["不限"],
            "job_hopping_tolerance": job_hopping_tolerance,
            "big_tech_preference": big_tech_preference,
            "required_soft_skills": required_soft_skills
        }
    
    def extract_bonus_points(self, jd_text: str) -> List[str]:
        """提取加分项"""
        bonus_keywords = [
            ('开源贡献', ['开源', 'github', 'contribution']),
            ('技术博客', ['博客', 'blog', '技术分享', '写作']),
            ('英语流利', ['英语', 'english', '口语', 'toefl', 'ielts']),
            ('算法竞赛', ['acm', '竞赛', 'leetcode', '算法题']),
            ('项目管理', ['pmp', '项目管理', 'scrum', 'agile']),
            ('海外经验', ['海外', '国外', 'international', '留学'])
        ]
        
        bonus_points = []
        jd_lower = jd_text.lower()
        for bonus, keywords in bonus_keywords:
            if any(keyword in jd_lower for keyword in keywords):
                bonus_points.append(bonus)
        
        return bonus_points
    
    def parse_jd_comprehensive(self, jd_text: str) -> Dict[str, Any]:
        """综合解析JD，生成完整画像"""
        if not jd_text or not isinstance(jd_text, str):
            return {"error": "Invalid input"}
        
        hard_req = self.extract_hard_requirements(jd_text)
        soft_req = self.extract_soft_requirements(jd_text)
        bonus_points = self.extract_bonus_points(jd_text)
        
        # 生成关键词基础
        base_keywords = hard_req["tech_stack"].copy()
        if hard_req["education"] != "不限":
            base_keywords.append(hard_req["education"])
        if hard_req["years_experience"] > 0:
            base_keywords.append(f"{hard_req['years_experience']}年经验")
        
        return {
            "core_profile": {
                "hard_requirements": hard_req,
                "soft_requirements": soft_req,
                "bonus_points": bonus_points
            },
            "base_keywords": base_keywords,
            "summary": f"职位要求: {len(hard_req['tech_stack'])}项技术栈, {hard_req['years_experience']}年经验, {hard_req['education']}学历"
        }

class KeywordSemanticMatrix:
    def __init__(self):
        # 预定义的语义扩展词库（简化版，实际可集成外部API）
        self.semantic_expansions = {
            'Python': ['python开发', 'python工程师', '后端开发', 'web开发', '数据科学'],
            'JavaScript': ['前端开发', 'javascript工程师', 'web开发', '全栈开发', 'react开发'],
            'Java': ['java开发', 'java工程师', '后端开发', 'spring开发', '企业级应用'],
            'React': ['react开发', '前端工程师', 'ui开发', 'web开发', 'javascript框架'],
            '机器学习': ['ml工程师', '数据科学家', '算法工程师', 'ai开发', '深度学习'],
            '数据库': ['dba', '数据库开发', '数据工程师', 'sql优化', '数据架构'],
            '云计算': ['云工程师', 'devops', '系统架构', '基础设施', '云原生'],
            '本科': ['学士学位', '大学本科', '本科学历', '四年制大学'],
            '硕士': ['硕士学位', '研究生', '硕士学历', '研究生学历'],
            '3年经验': ['中级工程师', '资深开发', '技术专家', '独立开发'],
            '5年经验': ['高级工程师', '技术主管', '架构师', '技术负责人']
        }
    
    def build_keyword_pyramid(self, base_keywords: List[str]) -> Dict[str, Any]:
        """构建关键词金字塔结构"""
        if not base_keywords:
            return {"error": "No base keywords provided"}
        
        # 顶层：精准搜索（原始关键词 + 最相关扩展）
        top_layer = []
        for kw in base_keywords[:3]:  # 取前3个核心关键词
            top_layer.append(kw)
            if kw in self.semantic_expansions:
                top_layer.extend(self.semantic_expansions[kw][:1])  # 每个取1个最相关
        
        # 腰部：跨界搜索（更多语义扩展）
        middle_layer = []
        for kw in base_keywords:
            if kw in self.semantic_expansions:
                middle_layer.extend(self.semantic_expansions[kw][1:3])  # 取第2-3个扩展
            else:
                # 通用扩展
                middle_layer.extend([f"{kw}相关", f"{kw}领域"])
        
        # 底部：潜力搜索（更广泛的通用词汇）
        bottom_layer = [
            "编程", "软件工程", "计算机科学", "算法", "数据结构",
            "学习能力强", "逻辑思维", "问题解决", "团队协作", "创新思维"
        ]
        
        # 去重并限制数量
        top_layer = list(dict.fromkeys(top_layer))[:5]
        middle_layer = list(dict.fromkeys(middle_layer))[:8]
        bottom_layer = list(dict.fromkeys(bottom_layer))[:10]
        
        return {
            "pyramid_structure": {
                "top_precision": {
                    "purpose": "找最匹配的",
                    "keywords": top_layer,
                    "search_strategy": "精确匹配，高权重"
                },
                "middle_cross": {
                    "purpose": "找可以跨界的", 
                    "keywords": middle_layer,
                    "search_strategy": "模糊匹配，中等权重"
                },
                "bottom_potential": {
                    "purpose": "找能转型的",
                    "keywords": bottom_layer,
                    "search_strategy": "广泛匹配，低权重但覆盖广"
                }
            },
            "total_keywords": len(top_layer) + len(middle_layer) + len(bottom_layer)
        }

# 初始化引擎
jd_parser = JDParseEngine()
keyword_matrix = KeywordSemanticMatrix()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze-jd', methods=['POST'])
def api_analyze_jd():
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '')
        result = jd_parser.parse_jd_comprehensive(jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/generate-keyword-matrix', methods=['POST'])
def api_generate_keyword_matrix():
    try:
        data = request.get_json()
        base_keywords = data.get('base_keywords', [])
        if isinstance(base_keywords, str):
            # 如果传入的是字符串，尝试解析为列表
            base_keywords = [kw.strip() for kw in base_keywords.split(',') if kw.strip()]
        
        result = keyword_matrix.build_keyword_pyramid(base_keywords)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/match-resume', methods=['POST'])
def api_match_resume():
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '')
        resume_text = data.get('resume_text', '')
        
        if not jd_text or not resume_text:
            return jsonify({"error": "Both JD and resume text are required"}), 400
        
        # 简单的简历匹配（后续会增强）
        jd_words = set(re.findall(r'\b[A-Za-z\u4e00-\u9fff]{2,}\b', jd_text.lower()))
        resume_words = set(re.findall(r'\b[A-Za-z\u4e00-\u9fff]{2,}\b', resume_text.lower()))
        
        common_words = jd_words.intersection(resume_words)
        match_percentage = 0
        if len(jd_words) > 0:
            match_percentage = round((len(common_words) / len(jd_words)) * 100, 2)
        
        return jsonify({
            "match_percentage": match_percentage,
            "common_keywords": list(common_words)[:15],
            "jd_keywords_count": len(jd_words),
            "resume_keywords_count": len(resume_words),
            "message": f"Resume matches {match_percentage}% of the job description keywords."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
