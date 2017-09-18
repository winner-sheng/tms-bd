# -*- coding: utf-8 -*-
import decimal

import simplejson

__author__ = 'Winsom'


SCENARIO_GLOBAL = 0
SCENARIO_STORE_GLOBAL = 20
# SCENARIO_COUPON = 60
SCENARIO_STORE_SPECIFIC = 30
SCENARIO_SUPPLIER_SPECIFIC = 40
SCENARIO_PRODUCT_SPECIFIC = 50
SCENARIO_USER_SPECIFIC = 60
SCENARIO_SHIP_FEE = 90
APPLY_TO_SCENARIO = (
    (SCENARIO_GLOBAL, u'普通全局计费/优惠规则'),
    # (SCENARIO_STORE_GLOBAL, u'门店优惠码'),
    # (SCENARIO_COUPON, u'特定优惠码'),
    (SCENARIO_STORE_SPECIFIC, u'特定门店优惠'),
    (SCENARIO_SUPPLIER_SPECIFIC, u'特定供应商优惠'),
    (SCENARIO_PRODUCT_SPECIFIC, u'特定商品优惠'),
    (SCENARIO_USER_SPECIFIC, u'特定用户优惠'),
    (SCENARIO_SHIP_FEE, u'邮费计算'),
)


class CouponRule(object):
    description = u'优惠/计费规则'
    required_fields = ['comment']

    def __init__(self, coupon_setting):
        if not coupon_setting.setting:
            raise ValueError(u'无效的规则配置！')

        # 初始化设置
        if isinstance(coupon_setting.setting, basestring):
            try:
                setting = simplejson.loads(coupon_setting.setting)
            except:
                raise ValueError(u'规则配置不正确（请使用json格式）')
        else:
            setting = coupon_setting.setting

        if isinstance(setting, dict):
            self.coupon_setting = coupon_setting
            self.setting = setting
        else:
            raise ValueError(u'请使用json格式(如{"key": "value"}样式)配置规则')

        self.validate()

    def __unicode__(self):
        return u'优惠/计费规则'

    def validate(self):
        if not self.setting or not isinstance(self.setting, dict):
            raise ValueError(u'无效的规则配置！')

        error = []

        if 'comment' in self.setting and (':' in self.setting['comment'] or ';' in self.setting['comment']):
            error.append(u'"comment"参数中不得使用英文冒号":"或英文分号";"符号')

        for field in self.required_fields:
            if field not in self.setting:
                error.append(u'缺少配置项（属性名："%s"）' % field)

        if self.coupon_setting.is_store_specific:
            if 'stores' not in self.setting or not isinstance(self.setting['stores'], list) \
                    or len(self.setting['stores']) == 0:
                error.append(u'特定门店适用的规则，请指定门店列表，数组格式（形如: "stores": ["code1", "code2"]）')

        if self.coupon_setting.is_supplier_specific:
            if 'suppliers' not in self.setting or not isinstance(self.setting['suppliers'], list) \
                    or len(self.setting['suppliers']) == 0:
                error.append(u'特定供应商适用的规则，请指定供应商列表，数组格式（形如: "suppliers": ["code1", "code2"]）')

        if self.coupon_setting.is_product_specific:
            if 'products' not in self.setting or not isinstance(self.setting['products'], list) \
                    or len(self.setting['products']) == 0:
                error.append(u'特定商品适用的规则，请指定商品列表，数组格式（形如: "products": ["code1", "code2"]）')

        # if self.coupon_setting.apply_to == SCENARIO_COUPON:
        #     if not self.setting.get('coupon'):
        #         error.append(u'特定优惠码的场景，请指定优惠码（形如: "coupon": "优惠码"）')

        if len(error) > 0:
            raise ValueError("，".join(error))

        return True

    def render_comment(self, off_value, supplier=None, product=None):
        """
        处理要展示给用户的最终优惠说明，末尾附上优惠金额（与前面提示之间以":"分隔）
        """
        comment = "%s:%s;" % (self.setting['comment'].replace("{off_value}", str(off_value)), -off_value)
        if supplier and "{supplier}" in comment:
            comment = comment.replace("{supplier}", supplier)
        if product and "{product}" in comment:
            comment = comment.replace("{product}", product)
        return comment

    def calc(self, cart):
        """
        计算购物车费用
        :param cart:
          - cart, 购物车
        :return:
        返回{'effective': True, 'cart': cart}， effective表示是否生效
        """
        raise NotImplementedError(u'需要实现calc方法！')


class SimpleReductionRule(CouponRule):
    """
    参数设置格式（以下，花括号及花括号内的文字，应保存在“优惠规则”的配置一栏）：
    {
        "reduction": 10,
        "threshold": 100,
        "comment": "商城试运营，每笔订单立减10元"
    }
    参数说明：
    - reduction，用于优惠计算，如10是指用户购物金额减10，不含邮费
    - threshold，用于条件限制，即满多少金额才执行优惠
    - comment，用于显示优惠说明，如果需要显示免除的费用金额，可在字符串中使用{off_value}占位符
    如果选择应用于“特定供应商”，则需要包含"suppliers"参数，参数值为对应的供应商编码数组。
        如["TWOHOU"] (数组必须包含方括号)
    如果选择应用于“特定店铺”，则需要包含"stores"参数，参数值为对应的店铺编码数组。
        如["cnbjbjb103", "cnahhfb359"] (数组必须包含方括号)
    如果选择应用于“特定商品”，则需要包含"products"参数，参数值为对应的商品编码数组。
        如["P150629938HEN", "P150629DU462T"] (数组必须包含方括号)
    """
    description = u'每笔订单立减X元'
    required_fields = CouponRule.required_fields + ['reduction']

    def __unicode__(self):
        return u'每笔订单立减X元'

    def calc(self, cart):
        effective = False
        reduction = decimal.getcontext().create_decimal(self.setting['reduction'])
        threshold = int(self.setting.get('threshold', 0))
        if self.coupon_setting.is_supplier_specific:
            suppliers = {}
            all_supplier = 'all' in self.setting['suppliers']  # 适用于所有供应商
            # 按商品供应商归并统计
            for item in cart['items']:
                supplier_code = item['product']['supplier']['code'] if item['product']['supplier'] else ''
                if supplier_code not in self.setting['suppliers'] and not all_supplier:
                    is_multiple = False
                    for code in self.setting['suppliers']:
                        if ',' in code:  # 多个供应商编码合并的情形
                            if supplier_code in code.split(','):
                                supplier_code = code  # 使用组合编码
                                is_multiple = True
                                break

                    if not is_multiple:
                        continue  # 忽略非特定供应商
                if supplier_code not in suppliers:
                    suppliers[supplier_code] = {"shop_amount": item['item_shop_amount'],
                                                "ship_fee": item['ship_fee']}
                else:
                    suppliers[supplier_code]["shop_amount"] += item['item_shop_amount']
                    suppliers[supplier_code]["ship_fee"] += item['ship_fee']

            for k, v in suppliers.items():
                if not threshold or not threshold > 0 or v['shop_amount'] >= threshold > 0:
                    if v['shop_amount'] > reduction:
                        cart['pay_off'] += reduction
                    else:
                        cart['pay_off'] += cart['shop_amount']  # 最多优惠额度为商品总额，不含邮费
                    cart['pay_off_comment'] += self.render_comment(reduction)
                    effective = True

        elif self.coupon_setting.is_product_specific:
            all_product = 'all' in self.setting['products']
            for item in cart['items']:
                if item['product']['code'] in self.setting['products'] or all_product:
                    if not threshold or not threshold > 0 or item['item_shop_amount'] >= threshold > 0:
                        effective = True
                        if item['item_shop_amount'] > reduction:
                            cart['pay_off'] += reduction
                        else:
                            cart['pay_off'] += item['item_shop_amount']
                        cart['pay_off_comment'] += self.render_comment(reduction)

        else:
            if not threshold or not threshold > 0 or cart['shop_amount'] >= threshold > 0:
                effective = True
                if cart['shop_amount'] - cart['pay_off'] > reduction:
                    cart['pay_off'] += reduction
                else:
                    cart['pay_off'] += cart['shop_amount']
                cart['pay_off_comment'] += self.render_comment(reduction)

        return {'effective': effective, 'cart': cart}


class PercentReductionRule(CouponRule):
    """
    参数设置格式（以下，花括号及花括号内的文字，应保存在“优惠规则”的配置一栏）：
    {
        "reduction": 0.05,
        "threshold": 100,
        "comment": "商城试运营，全场九五折"
    }
    参数说明：
    - reduction，用于优惠计算，如5%是指用户购物金额乘以5%(免除部分)，不含邮费（注意：数值不要加引号）
    - threshold，用于条件限制，即满多少金额才执行优惠，整数金额
    - comment，用于显示优惠说明，如果需要显示免除的费用金额，需在字符串中使用{off_value}占位符
    如果选择应用于“特定供应商”，则需要包含"suppliers"参数，参数值为对应的供应商编码数组。
        如["TWOHOU"] (数组必须包含方括号)
    如果选择应用于“特定店铺”，则需要包含"stores"参数，参数值为对应的店铺编码数组。
        如["cnbjbjb103", "cnahhfb359"] (数组必须包含方括号)
    如果选择应用于“特定商品”，则需要包含"products"参数，参数值为对应的商品编码数组。
        如["P150629938HEN", "P150629DU462T"] (数组必须包含方括号)
    """
    description = u'XX折优惠'
    required_fields = CouponRule.required_fields + ['reduction']

    def __unicode__(self):
        return u'XX折优惠'

    def calc(self, cart):
        effective = False
        reduction = self.setting['reduction']
        threshold = int(self.setting.get('threshold', 0))
        if self.coupon_setting.is_supplier_specific:
            suppliers = {}
            all_supplier = 'all' in self.setting['suppliers']  # 适用于所有供应商
            # 按商品供应商归并统计
            for item in cart['items']:
                supplier_code = item['product']['supplier']['code'] if item['product']['supplier'] else ''
                if supplier_code not in self.setting['suppliers'] and not all_supplier:
                    is_multiple = False
                    for code in self.setting['suppliers']:
                        if ',' in code:  # 多个供应商编码合并的情形
                            if supplier_code in code.split(','):
                                supplier_code = code  # 使用组合编码
                                is_multiple = True
                                break

                    if not is_multiple:
                        continue  # 忽略非特定供应商
                if supplier_code not in suppliers:
                    suppliers[supplier_code] = {"shop_amount": item['item_shop_amount'],
                                                "ship_fee": item['ship_fee']}
                else:
                    suppliers[supplier_code]["shop_amount"] += item['item_shop_amount']
                    suppliers[supplier_code]["ship_fee"] += item['ship_fee']

            for k, v in suppliers.items():
                if not threshold or not threshold > 0 or v['shop_amount'] >= threshold > 0:
                    off_value = v['item_shop_amount'] * int(reduction * 100) / 100
                    cart['pay_off'] += off_value
                    cart['pay_off_comment'] += self.render_comment(off_value)
                    effective = True

        elif self.coupon_setting.is_product_specific:
            all_product = 'all' in self.setting['products']
            for item in cart['items']:
                if item['product']['code'] in self.setting['products'] or all_product:
                    if not threshold or not threshold > 0 or item['item_shop_amount'] >= threshold > 0:
                        effective = True
                        off_value = item['item_shop_amount'] * int(reduction * 100) / 100
                        cart['pay_off'] += off_value
                        cart['pay_off_comment'] += self.render_comment(off_value)

        else:
            if not threshold or not threshold > 0 or cart['shop_amount'] >= threshold > 0:
                effective = True
                off_value = cart['shop_amount'] * int(reduction * 100) / 100
                cart['pay_off'] += off_value
                cart['pay_off_comment'] += self.render_comment(off_value)
        return {'effective': effective, 'cart': cart}


class FreeShipPerAmountRule(CouponRule):
    """
    参数设置格式（以下，花括号及花括号内的文字，应保存在“优惠规则”的配置一栏）：
    {
        "max": 20,
        "min": 5,
        "threshold": 100,
        "reduction": 10, (待定)
        "comment": "消费满￥100免运费￥{off_value}"
    }
    参数说明：
    - "max", 可选，即邮费上限不超过指定金额，只支持整数
    - "min", 可选，即邮费下限不低于指定金额（如果设置了threshold，超过免邮费的情形不在此例），只支持整数
    - threshold，满多少元免运费，如果设为0，则不论多少消费，运费全免 （该设置优先级高于max/min设置），只支持整数
    - reduction, 如果指定减免邮费数额
    - comment，用于显示优惠说明，{off_value}用来替换被免除的运费金额，
    如果选择应用于“特定供应商”，则需要包含"suppliers"参数，参数值为对应的供应商编码数组。
        如["TWOHOU"] (数组必须包含方括号)
    如果选择应用于“特定店铺”，则需要包含"stores"参数，参数值为对应的店铺编码数组。
        如["cnbjbjb103", "cnahhfb359"] (数组必须包含方括号)
    如果选择应用于“特定商品”，则需要包含"products"参数，参数值为对应的商品编码数组。
        如["P150629938HEN", "P150629DU462T"] (数组必须包含方括号)
    """
    description = u'根据消费金额计算运费'
    required_fields = CouponRule.required_fields + ['threshold']

    def __unicode__(self):
        return u'根据消费金额计算运费'

    def calc(self, cart):
        effective = False
        if cart.get('self_pick') == "1":  # 如果是自提的情况，免运费，直接订单中减，此处不做处理
            return {'effective': effective, 'cart': cart}

        threshold = int(self.setting.get('threshold', 0))
        if cart['ship_fee_amount'] <= 0:
            return False

        if self.coupon_setting.is_supplier_specific:
            suppliers = {}
            all_supplier = 'all' in self.setting['suppliers']  # 适用于所有供应商
            # 按商品供应商归并统计
            for item in cart['items']:
                if item['product']['supplier']:
                    supplier_code = item['product']['supplier']['code']
                else:
                    continue  # 忽略无供应商的商品
                if supplier_code not in self.setting['suppliers'] and not all_supplier:
                    is_multiple = False
                    for code in self.setting['suppliers']:
                        if ',' in code:  # 多个供应商编码合并的情形
                            if supplier_code in code.split(','):
                                supplier_code = code  # 使用组合编码
                                is_multiple = True
                                break

                    if not is_multiple:
                        continue  # 忽略非特定供应商
                if supplier_code not in suppliers:
                    suppliers[supplier_code] = {"shop_amount": item['item_shop_amount'],
                                                "ship_fee": item['ship_fee']}
                else:
                    suppliers[supplier_code]["shop_amount"] += item['item_shop_amount']
                    suppliers[supplier_code]["ship_fee"] += item['ship_fee']

            for k, v in suppliers.items():
                if v['shop_amount'] >= threshold > 0:
                    cart['ship_fee_off'] += v['ship_fee']  # 免除指定供应商的邮费
                    cart['pay_off_comment'] += self.render_comment(v['ship_fee'])
                    effective = True
                else:
                    if 'max' in self.setting and v['ship_fee'] > int(self.setting['max']):
                        # 免除指定供应商的邮费超出上限部分金额
                        off_value = v['ship_fee'] - int(self.setting['max'])
                        cart['ship_fee_off'] += off_value
                        cart['pay_off_comment'] += self.render_comment(off_value)
                        effective = True
                    if 'min' in self.setting and v['ship_fee'] < int(self.setting['min']):
                        # 加上指定供应商的邮费低于下限部分金额
                        off_value = v['ship_fee'] - int(self.setting['min'])
                        cart['ship_fee_off'] += off_value
                        cart['pay_off_comment'] += self.render_comment(off_value)
                        effective = True

        elif self.coupon_setting.is_product_specific:
            all_product = 'all' in self.setting['products']
            for item in cart['items']:
                if item['product']['code'] in self.setting['products'] or all_product:
                    if item['item_shop_amount'] >= threshold > 0:
                        effective = True
                        cart['ship_fee_off'] += item['ship_fee']  # 免除指定商品的邮费
                        cart['pay_off_comment'] += self.render_comment(item['ship_fee'])
                    else:
                        if 'max' in self.setting and item['ship_fee'] > int(self.setting['max']):
                            # 免除指定商品的邮费超出上限部分金额
                            off_value = item['ship_fee'] - int(self.setting['max'])
                            cart['ship_fee_off'] += off_value
                            cart['pay_off_comment'] += self.render_comment(off_value)
                            effective = True
                        if 'min' in self.setting and item['ship_fee'] < int(self.setting['min']):
                            # 加上指定商品的邮费低于下限部分金额
                            off_value = item['ship_fee'] - int(self.setting['min'])
                            cart['ship_fee_off'] += off_value
                            cart['pay_off_comment'] += self.render_comment(off_value)
                            effective = True

        else:
            if cart['shop_amount'] >= threshold > 0:
                effective = True
                cart['ship_fee_off'] = cart['ship_fee_amount']  # 免除整笔订单的邮费
                cart['pay_off_comment'] += self.render_comment(cart['ship_fee_amount'])
            else:
                if 'max' in self.setting and cart['ship_fee_amount'] > int(self.setting['max']):
                    # 免除指定供应商的邮费超出上限部分金额
                    off_value = cart['ship_fee_amount'] - int(self.setting['max'])
                    cart['ship_fee_off'] += off_value
                    cart['pay_off_comment'] += self.render_comment(off_value)
                    effective = True
                if 'min' in self.setting and cart['ship_fee_amount'] < int(self.setting['min']):
                    # 加上指定供应商的邮费低于下限部分金额
                    off_value = cart['ship_fee_amount'] - int(self.setting['min'])
                    cart['ship_fee_off'] += off_value
                    cart['pay_off_comment'] += self.render_comment(off_value)
                    effective = True

        return {'effective': effective, 'cart': cart}


# class FreeShipPerAmountBySupplierRule(CouponRule):
#     """
#     参数设置格式（以下，花括号及花括号内的文字，应保存在“优惠规则”的配置一栏）：
#     {
#         "max": 20,
#         "min": 5,
#         "threshold": 100,
#         "comment": "同一商户最低运费￥5，最高￥20，消费满￥100免运费"
#     }
#     参数说明：
#     - "max", 可选，即邮费上限不超过指定金额
#     - "min", 可选，即邮费下限不低于指定金额（如果设置了threshold，超过免邮费的情形不在此例）
#     - threshold，满多少元免运费，如果设为0，则不论多少消费，运费全免 （该设置优先级高于max/min设置）
#     - comment，用于显示优惠说明，{off_value}用来替换被免除的运费金额，
#     如果选择应用于“特定供应商”，则需要包含"suppliers"参数，参数值为对应的供应商编码数组。
#         如["TWOHOU"] (数组必须包含方括号)
#     如果选择应用于“特定店铺”，则需要包含"stores"参数，参数值为对应的店铺编码数组。
#         如["cnbjbjb103", "cnahhfb359"] (数组必须包含方括号)
#     如果选择应用于“特定商品”，则需要包含"products"参数，参数值为对应的商品编码数组。
#         如["P150629938HEN", "P150629DU462T"] (数组必须包含方括号)
#     """
#     description = u'同一商户消费满XX元免运费（邮费计算）'
#     required_fields = CouponRule.required_fields + ['threshold']
#
#     def __unicode__(self):
#         return u'同一商户消费满XX元免运费'
#
#     # def validate(self):
#     #     super(FreeShipPerAmountBySupplierRule, self).validate()
#     #     if self.coupon_setting.is_supplier_specific:
#     #         raise ValueError('该计费规则不适用于特定商户/特定商品，请使用【%s】' % FreeShipPerAmountRule.description)
#
#     def calc(self, cart):
#         effective = False
#         suppliers = {}
#         for item in cart['items']:
#             supplier_code = item['product']['supplier']['code'] if item['product']['supplier'] else ''
#             if supplier_code not in suppliers:
#                 suppliers[supplier_code] = {"shop_amount": item['pcs']*item['deal_price'], "ship_fee": item['ship_fee']}
#             else:
#                 suppliers[supplier_code]["shop_amount"] += item['pcs']*item['deal_price']
#                 suppliers[supplier_code]["ship_fee"] += item['ship_fee']
#
#         for k, v in suppliers.items():
#             if 'threshold' in self.setting and v['shop_amount'] >= int(self.setting['threshold']):
#                 cart['ship_fee_amount'] -= v['ship_fee']  # 免除指定供应商的邮费
#                 cart['pay_off_comment'] += self.render_comment(v['ship_fee'])
#                 effective = True
#             else:
#                 if 'max' in self.setting and v['ship_fee'] > int(self.setting['max']):
#                     # 免除指定供应商的邮费超出上限部分金额
#                     cart['ship_fee_amount'] -= v['ship_fee'] - int(self.setting['max'])
#                     cart['pay_off_comment'] += self.render_comment(v['ship_fee'])
#                     effective = True
#                 if 'min' in self.setting and v['ship_fee'] < int(self.setting['min']):
#                     # 加上指定供应商的邮费低于下限部分金额
#                     cart['ship_fee_amount'] += int(self.setting['min']) - v['ship_fee']
#                     cart['pay_off_comment'] += self.render_comment(v['ship_fee'])
#                     effective = True
#
#         return {'effective': effective, 'cart': cart}


RULE_MAP = {
    'SimpleReductionRule': SimpleReductionRule,
    'PercentReductionRule': PercentReductionRule,
    # 'SimpleFreeShipRule': SimpleFreeShipRule,
    'FreeShipPerAmountRule': FreeShipPerAmountRule,
    # 'FreeShipPerAmountBySupplierRule': FreeShipPerAmountBySupplierRule,
}


