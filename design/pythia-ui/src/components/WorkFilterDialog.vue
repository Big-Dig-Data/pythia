<i18n src="@/locales/dialog.yaml"></i18n>
<i18n lang="yaml">
en:
  work_filter: Work filter
  yop: Year of publication

cs:
  work_filter: Filtr děl
  yop: Rok vydání
</i18n>

<template>
  <v-card>
    <v-card-title>{{ $t("work_filter") }}</v-card-title>

    <v-card-text>
      <v-container>
        <v-row>
          <v-col cols="auto">
            <WorkLanguageSelector />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="auto">
            <OwnerInstitutionSelector />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="auto">
            <WorkTypeSelector />
          </v-col>
        </v-row>
        <v-row dense>
          <v-col cols="auto">
            <h4>{{ $t("yop") }}</h4>
            <YOPRangeSelector />
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="$emit('close')">{{ $t("close") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import WorkLanguageSelector from "./WorkLanguageSelector";
import YOPRangeSelector from "./YOPRangeSelector";
import OwnerInstitutionSelector from "./OwnerInstitutionSelector";
import WorkTypeSelector from "./WorkTypeSelector";

export default {
  name: "WorkFilterDialog",
  components: {
    WorkLanguageSelector,
    YOPRangeSelector,
    OwnerInstitutionSelector,
    WorkTypeSelector,
  },
};
</script>

<style scoped></style>
