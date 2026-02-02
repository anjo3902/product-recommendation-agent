// Clean formatting function with only safe ASCII and common emojis
// This replaces the formatOrchestratorResponse function

const formatOrchestratorResponse = (result) => {
    if (!result.success || !result.products || result.products.length === 0) {
        return 'I searched but could not find any products matching your query. Please try different keywords.';
    }

    const products = result.products;
    const comparison = result.comparison;
    const buyPlan = result.buy_plan;
    const aiSummary = result.summary?.ai_recommendation || '';

    // Count which agents returned data
    const agentsWorked = [];
    if (products.length > 0) agentsWorked.push('Product Search');
    if (products.some(p => p.review_analysis?.available)) agentsWorked.push('Review Analyzer');
    if (products.some(p => p.price_tracking?.available || p.price_analysis?.available)) agentsWorked.push('Price Tracker');
    if (comparison?.available) agentsWorked.push('Comparison');
    if (buyPlan?.available) agentsWorked.push('Buy Plan');

    let response = `\n`;
    response += `${'='.repeat(60)}\n`;
    response += `  AI SHOPPING ASSISTANT RESULTS\n`;
    response += `${'='.repeat(60)}\n\n`;

    response += `Active Agents: ${agentsWorked.join(', ')} (${agentsWorked.length}/5)\n\n`;
    response += `${'-'.repeat(60)}\n\n`;

    // SECTION 1: PRODUCT SEARCH RESULTS
    response += `\nPRODUCT SEARCH RESULTS (${products.length} found)\n`;
    response += `${'-'.repeat(60)}\n\n`;

    products.forEach((product, index) => {
        response += `${index + 1}. ${product.name}\n`;
        response += `   Price: Rs.${product.pricing?.current_price || product.price}`;
        if (product.pricing?.you_save > 0) {
            response += ` (Save Rs.${Math.round(product.pricing.you_save)} - ${product.pricing.discount_percent}% OFF)`;
        }
        response += `\n`;
        response += `   Rating: ${product.ratings?.average_rating || product.rating}/5 ${product.ratings?.rating_badge || ''}\n`;
        response += `   Reviews: ${product.ratings?.total_reviews || 0} customers\n`;
        response += `   Brand: ${product.brand || 'Unknown'}\n`;

        // Add detailed specifications - check both top level and original_data
        const keySpecs = product.key_specs || product.original_data?.key_specs;
        const specifications = product.specifications || product.original_data?.specifications;

        if (keySpecs && keySpecs.length > 0) {
            response += `\n   KEY SPECIFICATIONS:\n`;
            keySpecs.forEach(spec => {
                response += `      * ${spec}\n`;
            });
        } else if (specifications && Object.keys(specifications).length > 0) {
            response += `\n   TECHNICAL SPECIFICATIONS:\n`;

            // Format specifications with proper labels
            Object.entries(specifications).forEach(([key, value]) => {
                if (value && String(value).trim()) {
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    response += `      * ${label}: ${value}\n`;
                }
            });
        }

        // Add features if available - check both top level and original_data
        const features = product.features || product.original_data?.features;
        if (features && features.length > 0) {
            response += `\n   KEY FEATURES:\n`;
            features.slice(0, 5).forEach(feature => {
                response += `      + ${feature}\n`;
            });
        }

        response += `\n`;
    });

    response += `${'-'.repeat(60)}\n\n`;

    // SECTION 2: REVIEW ANALYSIS
    const hasReviews = products.some(p => p.review_analysis?.available);
    if (hasReviews) {
        response += `\nCUSTOMER REVIEW ANALYSIS\n`;
        response += `${'-'.repeat(60)}\n\n`;

        products.forEach((product, index) => {
            if (product.review_analysis?.available) {
                const review = product.review_analysis;
                response += `${index + 1}. ${product.name}\n\n`;
                response += `   Sentiment: ${review.sentiment}\n`;
                response += `   Trust Score: ${review.trust_score_percent}\n\n`;

                if (review.pros && review.pros.length > 0) {
                    response += `   WHAT CUSTOMERS LOVE:\n`;
                    review.pros.slice(0, 3).forEach(pro => {
                        response += `      + ${pro}\n`;
                    });
                    response += `\n`;
                }

                if (review.cons && review.cons.length > 0) {
                    response += `   WHAT TO WATCH OUT FOR:\n`;
                    review.cons.slice(0, 2).forEach(con => {
                        response += `      - ${con}\n`;
                    });
                    response += `\n`;
                }

                response += `\n`;
            }
        });

        response += `${'-'.repeat(60)}\n\n`;
    }

    // SECTION 3: PRICE TRACKING
    const hasPrices = products.some(p => p.price_tracking?.available || p.price_analysis?.available);
    if (hasPrices) {
        response += `\nPRICE TRACKING & DEALS\n`;
        response += `${'-'.repeat(60)}\n\n`;

        products.forEach((product, index) => {
            const priceData = product.price_tracking || product.price_analysis;
            if (priceData?.available) {
                response += `${index + 1}. ${product.name}\n\n`;
                response += `   Recommendation: ${priceData.recommendation}\n\n`;
                response += `   Price Statistics (${priceData.history_days || 30}-day trend):\n`;
                response += `      Current:  Rs.${Math.round(priceData.current_price)}\n`;
                response += `      Average:  Rs.${Math.round(priceData.average_price)}\n`;
                response += `      Lowest:   Rs.${Math.round(priceData.lowest_price)}\n`;
                response += `      Highest:  Rs.${Math.round(priceData.highest_price)}\n`;
                response += `      Trend: ${priceData.price_trend} (${priceData.price_change_percent > 0 ? '+' : ''}${priceData.price_change_percent.toFixed(1)}%)\n\n`;

                if (priceData.ai_recommendation) {
                    response += `   AI Recommendation:\n   ${priceData.ai_recommendation}\n\n`;
                }

                response += `\n`;
            }
        });

        response += `${'-'.repeat(60)}\n\n`;
    }

    // SECTION 4: PRODUCT COMPARISON
    if (comparison?.available && products.length >= 2) {
        response += `\nPRODUCT COMPARISON\n`;
        response += `${'-'.repeat(60)}\n\n`;

        response += `OVERALL WINNER: ${comparison.winner_name}\n`;
        response += `REASON: ${comparison.winner_reason}\n\n`;

        if (comparison.category_winners) {
            const cw = comparison.category_winners;
            response += `CATEGORY CHAMPIONS:\n\n`;

            if (cw.best_price) {
                response += `   Best Price: ${cw.best_price.product_name} - ${cw.best_price.price}\n`;
            }
            if (cw.best_rating) {
                response += `   Highest Rating: ${cw.best_rating.product_name} - ${cw.best_rating.rating}\n`;
            }
            if (cw.best_value) {
                response += `   Best Value: ${cw.best_value.product_name}\n`;
            }
            response += `\n`;
        }

        if (comparison.ai_comparison) {
            response += `AI INSIGHTS:\n`;
            response += `${'-'.repeat(60)}\n`;
            response += `${comparison.ai_comparison}\n`;
            response += `${'-'.repeat(60)}\n\n`;
        }

        response += `Scroll down for detailed comparison table\n\n`;
        response += `${'-'.repeat(60)}\n\n`;
    }

    // SECTION 5: PAYMENT PLAN
    if (buyPlan?.available) {
        response += `${'-'.repeat(60)}\n`;
        response += `  PAYMENT PLAN OPTIMIZER\n`;
        response += `${'-'.repeat(60)}\n\n`;

        response += `For: ${buyPlan.product_name}\n`;
        response += `Price: Rs.${buyPlan.product_price}\n\n`;

        const rec = buyPlan.recommendations;
        if (rec) {
            response += `BEST PAYMENT OPTIONS:\n\n`;

            if (rec.best_instant_savings) {
                const bis = rec.best_instant_savings;
                response += `   Instant Discount: ${bis.bank} Card\n`;
                response += `      Save Rs.${bis.discount} - Pay only Rs.${buyPlan.product_price - bis.discount}\n\n`;
            }

            if (rec.best_cashback) {
                const bcb = rec.best_cashback;
                response += `   Best Cashback: ${bcb.bank}\n`;
                response += `      Get Rs.${bcb.cashback} cashback (${bcb.cashback_percent}%)\n\n`;
            }

            if (rec.best_emi) {
                const bei = rec.best_emi;
                response += `   Best EMI Plan: ${bei.tenure} months\n`;
                response += `      Rs.${bei.monthly_emi}/month | Bank: ${bei.bank}`;
                if (bei.interest === 0) response += ` (No Cost EMI!)`;
                response += `\n\n`;
            }

            if (rec.ai_recommendation) {
                response += `   AI Financial Advice:\n   ${rec.ai_recommendation}\n\n`;
            }
        }

        response += `${'-'.repeat(60)}\n\n`;
    }

    // SECTION 6: AI SUMMARY
    if (aiSummary) {
        response += `${'-'.repeat(60)}\n`;
        response += `  AI RECOMMENDATION SUMMARY\n`;
        response += `${'-'.repeat(60)}\n\n`;
        response += `${aiSummary}\n\n`;
        response += `${'-'.repeat(60)}\n\n`;
    }

    // Footer
    response += `ANALYSIS COMPLETE!\n\n`;
    response += `Analyzed ${products.length} product${products.length > 1 ? 's' : ''} using ${agentsWorked.length}/5 AI agents\n`;
    response += `Execution Time: ${result.execution_time_seconds || 'N/A'}s\n\n`;
    response += `Need Help? Ask me anything about these products!\n`;
    response += `${'='.repeat(60)}`;

    return response;
};

export default formatOrchestratorResponse;
