class EnvTestsSupport:
    def to_dict():
        return {
            "KOIKI_HOST": "https://testing_host",
            "WCFMMP_HOST": "https://wcfmmp_testing_host",
            "WCFMMP_USER": "test_wcfmmp_user",
            "WCFMMP_PASSWORD": "test_wcfmmp_password",
            "KOIKI_AUTH_TOKEN": "testing_auth_token",
            "KOIKI_ERROR_MAIL_RECIPIENTS": "test@test.com",
            "REDIS_URL": "rediss://test",
            "SUGARCRM_REST_URL": "https://test_sugarcrm_host",
            "SUGARCRM_USER": "test_sugarcrm_user",
            "SUGARCRM_PASSWORD": "test_sugarcrm_password",
            "SUGARCRM_MEMBERSHIP_ROLES": "^member^,^is_partner^",
            "WP_PARTNER_ROLE": "socia_opcions",
        }
